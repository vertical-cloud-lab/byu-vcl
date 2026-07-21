# 3D Printing SOP — Vertical Cloud Lab

Standard operating procedure for the lab's FDM 3D printers, including
**multi-material PLA + TPU** prints on the **Bambu Lab H2D**.

> **Scope:** This is a working resource for lab members. Edit it freely as we
> learn what works. Anything in _[square brackets]_ is a placeholder to be
> filled in with our specific hardware, contacts, or lab conventions.

- **Printer(s):** Bambu Lab H2D _(add others here as acquired)_
- **Slicer:** Bambu Studio _(recommended; OrcaSlicer is a compatible alternative)_
- **Lab location:** _[Lab #, Building]_
- **Primary contact:** _[name / email]_
- **Related:** [tensegrity-optimization #37](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/37)

---

## 1. Safety first

- **Read the [BYU Engineering SOP template](byu-engineering-sop-template.md)** and any
  BYU lab-safety documents in this repo before operating equipment unsupervised.
- **Hot surfaces.** The nozzles (up to ~300 °C) and heated bed (up to ~110 °C)
  cause burns. Do not reach into the build chamber while printing or immediately
  after. Let parts and the bed cool before removing.
- **Ventilation.** FDM printing emits ultrafine particles and VOCs. Keep the
  printer's enclosure closed during printing and run in a ventilated area. The
  H2D has a built-in air filter — check that the carbon filter is installed and
  not expired.
- **Moving parts.** Keep hands, hair, and tools clear of the gantry, toolhead,
  and cutter while the machine is powered and homing/printing.
- **Electrical & fire.** Do not leave long prints fully unattended overnight
  without following the lab's remote-monitoring rule below. Know where the
  nearest fire extinguisher and emergency stop are: _[location]_.
- **Tools.** Use the flush cutters, scraper, and pliers carefully; the bed
  scraper is sharp. Never use a metal scraper that can gouge the PEI plate.

**Emergency contacts** (from the BYU SOP template):

- University Police: 801-422-2222
- Risk Management: 801-422-4468
- College Health & Safety Officer: 801-422-6589

---

## 2. Materials overview

| Material | Typical nozzle | Bed  | Enclosure | Notes |
| -------- | -------------: | ---: | --------- | ----- |
| **PLA**  | 190–220 °C     | 35–55 °C | Open OK, door ajar to avoid heat creep | Easy, rigid, low warp. Keep dry-ish. |
| **TPU** (e.g., 95A) | 220–240 °C | 35–45 °C | Open OK | Flexible. **Print slow** and direct-drive only. Very moisture-sensitive. |

- **Verify the manufacturer's recommended temperatures** on the spool and in the
  Bambu Studio filament profile — the ranges above are starting points.
- **Dry filament matters.** TPU and, to a lesser extent, PLA absorb moisture,
  which causes stringing, popping, and weak layers. Dry TPU before critical
  prints _(≈ 60–70 °C for 6–12 h in a filament dryer / low oven)_. Store spools
  with desiccant.

### Why the H2D is well suited to PLA + TPU

The H2D has **two independent nozzles (dual extruder)**. This is the preferred
way to combine PLA and TPU: each material has its own direct-drive path, so soft
TPU never has to travel through a shared Bowtube/AMS buffer where it tends to
buckle. Assign PLA to one nozzle and TPU to the other.

> **Avoid running TPU through the AMS** unless using an AMS/profile explicitly
> rated for that TPU. Soft filaments jam in the AMS feed path. Feed TPU from an
> external spool holder into the direct-drive nozzle.

---

## 3. Before you print (checklist)

- [ ] Build plate is the right type for the material (textured PEI is a good
      default for both PLA and TPU) and is **clean** — wash with dish soap +
      water or wipe with IPA; avoid touching the surface with bare fingers.
- [ ] Correct filament loaded in the correct nozzle/slot, and the slicer's
      filament assignment matches physically what's loaded.
- [ ] Filament is dry (especially TPU) and feeding freely without tangles.
- [ ] Nozzles are clean; no stuck debris or "boogers" on the tips.
- [ ] Firmware and Bambu Studio are reasonably up to date.
- [ ] You have logged your print / reserved the machine per lab convention:
      _[sign-up sheet / calendar link]_.

---

## 4. Slicing workflow (Bambu Studio)

1. **Import geometry.** Open your STL/STEP/3MF in Bambu Studio and select the
   **Bambu Lab H2D** printer profile.
2. **Assign materials to nozzles.** In a multi-material project, map each object
   (or each modifier/part) to a filament: **PLA → nozzle 1, TPU → nozzle 2**
   (or per lab convention). Confirm the filament profiles' temperatures.
3. **Choose a base profile.** Start from a standard 0.20 mm profile and adjust.
   Save lab-tuned profiles back into this repo or a shared drive when you find
   good settings _(link: [placeholder])_.
4. **Slice, then inspect the preview.** Step through layers to check the
   material transitions, seams, and any purge/wipe towers.
5. **Estimate & sanity check.** Review time and filament estimates before
   committing to long prints.

### Suggested starting settings

| Setting | PLA | TPU |
| ------- | --- | --- |
| Layer height | 0.20 mm | 0.20 mm |
| Print speed (outer walls) | 100–200 mm/s | **15–30 mm/s** |
| Retraction | Default | Minimal / short |
| Flow (cooling) fan | High | Low–medium |
| Supports | As needed | Prefer designing to avoid; TPU supports are hard to remove |

> **Multi-material specifics:** expect a **purge/prime tower** and material-change
> purging. This wastes some filament but keeps colors/materials from bleeding.
> For a first test, the tensegrity workflow suggests something as simple as
> **alternating a few layers of TPU and PLA** to validate adhesion and the
> tool-change sequence before attempting a full part.

---

## 5. Running the print

1. **Send** the job via LAN / Bambu Studio / SD card (per lab preference).
2. **Watch the first layer.** This is the single most important step — confirm
   good bed adhesion and no nozzle collisions. Cancel and re-level/re-clean if
   the first layer looks poor.
3. **Confirm each nozzle deposits** on its first use in a multi-material job.
4. **Monitoring:** Enable the printer's camera and remote monitoring. Follow the
   lab rule for unattended prints: _[e.g., "prints > X hours require remote
   monitoring + notify #channel"]_.

### PLA + TPU bonding notes

- PLA and TPU do **not** chemically weld strongly. For durable multi-material
  parts, design **mechanical interlocks** (dovetails, holes/pockets the second
  material flows into, overlapping perimeters) rather than relying on a flat
  interface.
- Increasing interface overlap and slightly higher temperature at the boundary
  layers can improve adhesion — tune experimentally and record results.

---

## 6. After the print

- [ ] Let the bed cool; flex the plate to release the part (textured PEI).
- [ ] Remove purge/prime tower and supports; dispose of scrap in _[waste bin]_.
- [ ] Clean the plate and return it to the printer.
- [ ] Unload TPU if the next user needs the nozzle, or leave loaded per lab
      convention. Store TPU with desiccant.
- [ ] Wipe down the work area and return tools.
- [ ] Note anything odd (jams, failures, low filament) in _[log / issue tracker]_.

---

## 7. Troubleshooting

| Symptom | Likely cause | Try |
| ------- | ------------ | --- |
| First layer not sticking | Dirty/greasy plate, nozzle too high | Clean plate, re-level, lower Z offset slightly |
| TPU stringing / popping | Wet filament | Dry the TPU; reduce speed |
| TPU jam / grinding | Fed through AMS or too fast; retraction too high | Use direct-drive/external spool, slow down, reduce retraction |
| Layers separating (delamination) | Temp too low, drafts, moisture | Raise nozzle temp, close enclosure, dry filament |
| Multi-material color bleed | Insufficient purge | Increase purge volume / prime tower size |
| PLA/TPU interface splits | No mechanical bond | Redesign with interlocking geometry, increase overlap |
| Clogged nozzle | Debris, mixed materials, heat creep | Cold pull / hot clean per Bambu Lab guide |

---

## 8. References & resources

- Bambu Lab H2D user manual and wiki — _[add link]_
- Bambu Studio documentation — _[add link]_
- TPU printing guide (Bambu Lab) — _[add link]_
- BYU Engineering Lab Safety / Chemical Hygiene Plan — see PDFs in this repo
- Add tutorials/videos you found helpful here as you go:
  - _[link + one-line note]_

---

_Maintained by the Vertical Cloud Lab. Please open a PR to improve this SOP._

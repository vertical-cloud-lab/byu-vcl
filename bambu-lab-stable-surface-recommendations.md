# Bambu Lab Printer — Stable Surface / Workbench Recommendations

Reference notes for siting a Bambu Lab printer (X1 / P1 / A1 / H2D series) in
the lab. These follow Bambu Lab's official guidance plus widely-used community
best practices. The H2D is called out specifically because it is the model
currently being set up in the VCL (see #88).

## TL;DR

Use a **heavy, flat, level workbench that supports at least 2× the printer's
weight, does not flex or wobble, has clearance on all sides for airflow / the
AMS / door swing, and is not in direct sunlight or a dusty/humid spot.**

## 1. Flatness & stability

- Surface must be flat and stable; check with a spirit / bubble level.
- The bench must not noticeably flex or wobble during high-speed moves —
  Bambu Lab printers (especially CoreXY models like X1 / P1 / H2D) move fast
  and transmit significant vibration.
- Avoid lightweight or rolling carts, plastic tables, and unreinforced IKEA
  Lack-style tables.

## 2. Weight capacity

Use a bench rated to **at least 2×** the printer's weight (more if an AMS, AMS
HT, spool stacker, or enclosure is also sitting on it).

| Model     | Printer weight | Min. recommended bench rating |
|-----------|----------------|-------------------------------|
| A1 mini   | ~8 kg          | ~16 kg                        |
| A1        | ~11 kg         | ~22 kg                        |
| P1S / P1P | ~12 kg         | ~25 kg                        |
| X1C / X1E | ~14 kg         | ~30 kg                        |
| **H2D**   | **~31 kg**     | **≥ 50 kg** (per Bambu Lab)   |

## 3. Footprint & clearance

Leave space around the printer for airflow, cable routing, door / lid swing,
filament changes, and maintenance.

- General guidance: at least **10–15 cm (4–6 in)** on the back and sides;
  more if an AMS or enclosure is attached.
- Top: clear the full lid / hood travel.
- Do **not** block intake or exhaust vents.
- **H2D specifically**: Bambu recommends a workbench footprint of at least
  **600 mm × 700 mm** (printer body is 492 × 514 × 626 mm).

## 4. Vibration dampening

- The bench itself doing its job (mass + rigidity) matters more than any pad.
- If noise / resonance is still an issue, anti-vibration pads or a paver /
  concrete slab under the printer help.
- Do not place two printers on the same flexible surface — they will couple
  and degrade each other's prints.

## 5. Environment

- Indoor, dry, dust-free.
- Ambient temperature **10–30 °C** (Bambu's stated operating range).
- Out of direct sunlight (UV degrades filament and confuses the chamber
  camera / AI inspection).
- Away from strong drafts, HVAC vents blowing directly on the printer, and
  obvious vibration sources (washing machines, CNC mills, etc.).
- Ventilation: P1 / X1 / H2D series have HEPA + activated-carbon filters but
  still emit some VOCs / ultrafine particles, especially with ABS / ASA /
  PA-CF. Site them in a ventilated room or in/under a fume hood when
  possible; do not enclose them in a sealed cabinet without active venting.

## 6. Power

- **H2D**: up to **2200 W @ 220 V** or **1320 W @ 110 V** — make sure the
  outlet circuit can handle it. Prefer a dedicated outlet; do not daisy-chain
  on a power strip with other heavy loads.
- A1 / P1 / X1 series are lower power but still benefit from a dedicated /
  surge-protected outlet.

## 7. Lab-specific notes (VCL)

- Multiple AMS units (see #88) add weight and depth — confirm the bench is
  deep enough that the AMS does not overhang and that combined weight is
  still inside the 2× safety margin.
- If stacking AMS units (e.g. "Noodle Nexus" stacker referenced in #88),
  recheck the center of gravity and clearance to walls / shelves above.

## References

- Bambu Lab H2D — Technical Specifications: <https://bambulab.com/en-us/h2d/tech-specs>
- Bambu Lab Wiki — X1C unboxing / first use: <https://wiki.bambulab.com/en/x1/x1c-unboxing>
- Bambu Lab Wiki — P1 series first use: <https://wiki.bambulab.com/en/p1/first-use>
- Bambu Lab Wiki — A1 series first use: <https://wiki.bambulab.com/en/a1/first-use>

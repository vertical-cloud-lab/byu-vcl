# SEM/EDS polishing workflow — complete bill of materials

Everything named in [issue #110](https://github.com/vertical-cloud-lab/byu-vcl/issues/110) and in
the [polishing SOP](https://github.com/vertical-cloud-lab/byu-vcl/blob/5e5cdf9/SOP/sem-eds-polishing-sop.md), priced. Covers the grinding papers, the
polishing cloth and abrasives, the mounting compound, the solvents and glassware, the SEM stub prep,
and the vacuum hardware.

> **Prices are vendor list prices captured 2026-09-23**, before shipping and tax, US sites only.
> Every number in a **bold** cell was read off a live product page. Numbers marked *(est.)* are a
> range from comparable products, not a quote — treat them as budget placeholders.
>
> **Allied High Tech and LECO publish no online prices.** Both are quote-only, by phone or email.
> That matters here because *the items currently on the shelf are Allied and LECO parts* — so this
> document pairs each of them with a priced equivalent from a vendor that does publish.

## Part numbers, read off the labels

Not guessed. These come from the photos in the issue thread:

| Item | Brand & part no. | Size | Where it appears |
| --- | --- | --- | --- |
| Black Bakelite mounting powder | **LECO `811-110`** | 1 lb (454 g) | [issue photo 1](https://github.com/vertical-cloud-lab/byu-vcl/issues/110#issue-4471024294) |
| SiC grinding papers, plain back | **LECO `810-295/296/297-PRM`, `810-856-100`, `810-857-100`** | 12″ (305 mm), 100/box | issue photo 2 |
| Polishing cloth | **Allied `50-150-505`** — Imperial Adhesive Back Disc | 12″/300 mm, **Pk/10** | issue photo 3 |
| 1 µm alumina suspension | **Allied** — De-Agglomerated, refill bottle (`90-187550` = 32 oz) | 32 oz | issue photo 4 |
| 0.05 µm colloidal silica | **Allied `180-20000`** — Non-Crystallizing | 128 oz (3.8 L) | issue photo 5 |
| Acetone | **Macron `2435-06`** ChromAR | 1 L | issue photo 6 |
| Laboratory film | **Parafilm M** (Bemis), 4″ roll | — | issue photo 7 |
| Conductive silver paint | **Ted Pella `16062`** — PELCO Conductive Silver Paint | 30 g | [Gage, 2026-05-21](https://github.com/vertical-cloud-lab/byu-vcl/issues/110#issuecomment-4513047211) |
| Glass containers | BYU Chem Stores `0007734` (crystallization dish, 90×50 mm) + `0007746` (Petri, 100×20 mm w/ cover) | — | same comment |

Two corrections to the shopping list in the issue body, both from the labels:

- The **"one micrometer aluminum suspension"** is **alumina** (Al₂O₃), not aluminum.
- **`#50-150-505` is not an abrasive.** It is the Imperial *polishing cloth* — a low-napped rayon
  flock, adhesive back, **10 per pack, not 100**. It is what the 1 µm alumina runs on, and it is a
  different line item from the 320–1200 papers.

## Part A — Consumables

### A1. SiC grinding papers, 320 → 1200

Full comparison in [`sem-eds-polishing-grinding-discs-sourcing.md`](sem-eds-polishing-grinding-discs-sourcing.md).
Headline numbers, 12″ **plain back** (what the hold-down ring clamps — *not* PSA):

| Vendor | One box of 100, each of 320/400/600/800/1200 | 25 of each |
| --- | ---: | ---: |
| **Mark V Lab** (LECO replacement) | **$521** | — |
| OnPoint Abrasives CarbiPro | $730 | **$214** |
| Beta Diamond | $746 | — |
| PACE Technologies | $1,110 | — |
| Buehler CarbiMet/MicroCut | $1,483 | — |
| Allied / LECO | quote | quote |

One paper per grit per sample ⇒ a box of 100 is roughly 100 samples.

### A2. Polishing cloth — 12″, adhesive back

The SOP's "peel off the back to expose the sticky side" step. **PSA is correct here**, unlike the
grinding papers.

| Product | Pack | Price |
| --- | --- | ---: |
| **Allied `50-150-505` Imperial** — what the lab uses | Pk/10 | quote only |
| OnPoint **FinalFloc**, 12″ PSA — closest flock analogue | 10 | **$95** |
| OnPoint **SpecCloth**, 12″ PSA | 10 | **$105** |
| OnPoint MasterPlan / GoldStandard / ProDac / NoWeave / UltraViolet / MintPlus / ShortFinal | 10 | **$105** |
| OnPoint RedFelt | 10 | **$120** |
| PACE **TEXPAN** `TP-5012`, 12″ PSA | 10 | **$132** |

Allied describes Imperial as "low-napped, synthetic rayon flock with film backing… good all-purpose
final polishing cloth," which is the same class as OnPoint's FinalFloc and SpecCloth. **≈$9.50–13
per cloth**, and the SOP allows re-use *within a single alloy*, so this is not a per-sample cost.

### A3. 1 µm alumina suspension, de-agglomerated

| Product | Size | Price |
| --- | --- | ---: |
| **Allied `90-187550`** (32 oz) / `90-187585` (128 oz) / `90-187517` (16 oz) | — | quote only |
| OnPoint **Alumabrasive `ALS-321`**, 1 µm | 32 oz | **$72** |
| Mark V Lab **`AS1-32`**, 1 µm | 32 oz | **$92** |

### A4. 0.05 µm colloidal silica, non-crystallizing

For the vibratory-polishing step (SOP §6, still a stub). The Allied bottle on the shelf is a
**gallon**; that is a lot of silica for a lab that has not run the step yet.

| Product | 16 oz | 32 oz | 64 oz | 1 gal |
| --- | ---: | ---: | ---: | ---: |
| **Allied `180-20000`**, 0.05 µm non-crystallizing | — | — | — | quote only |
| OnPoint **ProPrep 2**, 0.04 µm *low-crystallizing* | **$22** | **$38** | **$64** | **$110** |
| OnPoint ProPrep, 0.04 µm standard | $20 | $34 | $60 | $105 |
| OnPoint SilverBullet CMP, 0.05 µm | $70 | $70 | $110 | $150 |
| PACE **SIAMAT 2**, 0.02 µm low-crystallizing | $29 | — | — | — |

**Buy the low-crystallizing grade.** Gage's cleaning note — "silicone crystals start forming
immediately," i.e. *silica* — is exactly the failure this grade exists to slow down. It does not
remove the need to keep the surface wet; it buys time.

### A5. Mounting compound

| Product | Size | Price |
| --- | --- | ---: |
| **LECO `811-110`** black Bakelite — what's on the shelf | 1 lb | quote only |
| **Mark V `MK-811-111`** black Bakelite, sold as the LECO replacement | 5 lbs | **$40** |
| OnPoint PhenoMount black phenolic | 5 lbs | not captured |
| PACE `CM-2001B` phenolic powder, black | 5 lbs | not captured |

At ¾ scoop per puck this is the cheapest thing in the whole workflow. 5 lb ≈ 80–100 mounts.

**Worth flagging against Gage's "metal pucks + superglue" idea:** Bakelite is cheap but it is also
the step that ruined a sample when a pellet tipped over ([Ronnie, 2026-09-23](https://github.com/vertical-cloud-lab/byu-vcl/issues/110#issuecomment-5802068338)),
and it is the reason the Kapton tape was bought. Glue-to-puck skips mounting-press time, tipping,
and demolding entirely. Pucks are not a catalog item — 1.25″ round aluminium or steel stock cut to
~10 mm is a machine-shop job, cheaper than any metallography vendor's holder.

### A6. Solvents, film, and glassware

Order these through **BYU Chem Stores** rather than a metallography vendor; that is where the glass
dishes already came from, and it avoids a new supplier on meorders.

| Item | Spec | Price |
| --- | --- | ---: |
| Glass container sets (crystallization dish + Petri w/ cover) | `0007734` + `0007746` | **$75 for 3 sets** (Gage's quote) |
| Ethanol, 200 proof | 4 L | ~$58 *(est.)* |
| Methanol, ACS | 4 L | ~$45–60 *(est.)* |
| Acetone, ACS/ChromAR | 4 L | ~$32–55 *(est.)* |
| Wash bottles, Nalgene right-to-know, labelled | 500 mL ×3 (acetone / ethanol / methanol) | ~$11 ea *(est.)* |
| **Parafilm M `PM996`** | 4″ × 125 ft roll | **$42.02** Walmart / **$49.00** Cole-Parmer |

The solvent lines are the only *(est.)* entries that matter for the total, and they are small. Chem
Stores' internal price will beat any list price quoted here — get the real numbers when ordering.

### A7. SEM stub preparation

| Item | Pack | Price |
| --- | --- | ---: |
| **Ted Pella `16111`** aluminium pin stub, Ø12.7 mm × 8 mm | 50 | **$18** |
| | 100 | **$34** |
| | 500 | **$165** |
| | 1000 | **$310** |
| **Ted Pella `16062`** PELCO Conductive Silver Paint | 30 g | **$157.65** |
| **Ted Pella `16062-15`**, same paint | 15 g | **$58.05** |
| Ted Pella `16031` PELCO Colloidal Silver — cheaper alternative | 30 g | **$112.35** |
| Ted Pella `16034` PELCO Colloidal Silver | 15 g | **$57.65** |
| Ted Pella `16084-1` carbon conductive tabs, 12 mm | 100 | quote |

**Order silver paint direct from Ted Pella, not through Fisher.** Fisher lists the same 30 g bottle
(`NC0683430`) at **$193.12** against Ted Pella's own **$157.65** — a 22% markup on an identical part.
The stubs show the same pattern: Ted Pella $18/50, Fisher $35.85/50.

**Start with the 15 g bottle.** 30 g of silver paint is a career's worth at three dabs per stub, and
it skins over once opened.

### A8. Tape and shop supplies

| Item | Status | Price |
| --- | --- | ---: |
| Kapton (polyimide) tape | **already received** — [ORDER 12789](https://meorders.byu.edu/order/12789), in the cabinet | — |
| "Electroplated tape" for the cloth pull-tab (3M `470`, tan vinyl, 1″×36 yd) | 3M sells by the case; no single-roll list price found | not captured |
| PTFE thread-seal tape (the vacuum fittings need two wraps per joint) | hardware store | ~$3 *(est.)* |
| Nitrile gloves, lint-free wipes, compressed air | lab stock | — |

The pull-tab in SOP §6.2 does not need a special tape. **Use the Kapton already in the cabinet** and
close this line item.

## Part B — Hardware (one-time)

| Item | Detail | Price |
| --- | --- | ---: |
| **Vacuum gauge** for the desiccator | 2.5″ dial, 0 to −30 inHg, ¼″ NPT, glycerin-filled | **$15–25** *(est.)* |
| **Vacuum pump** — Pittsburgh `61176`, 3 CFM two-stage | Harbor Freight | **$139.99** |
| Pittsburgh `61245`, 2.5 CFM single-stage | Harbor Freight | **$99.99** |
| Oil-free diaphragm pump (lab-grade alternative) | quieter, no oil changes, shallower vacuum | not captured |
| Vibratory polisher (SOP §6) | Buehler **VibroMet 2 is discontinued**; PACE GIGA-S is the current equivalent | quote only |
| Diamond wafering blade | currently checked out from the PSC per blade | not priced |

Three notes:

1. **The two-stage pump is overkill and the right buy anyway.** A desiccator needs perhaps −28 inHg;
   the two-stage reaches ~22 microns. At $140 the margin costs $40 over the single-stage, and it
   means the pump is never the limiting factor. A **diaphragm pump is the better lab citizen**
   (oil-free, no oil mist, no maintenance), but costs several times more — worth pricing if this
   pump will live in a room where people work.
2. **The gauge is the item that actually changes behaviour.** Without it, "when do we re-evacuate?"
   has no answer and the chamber gets pumped on a hunch. It is the cheapest line in this document.
3. The vacuum-chamber thread has moved to
   [vertical-cloud-lab/caliber#16](https://github.com/vertical-cloud-lab/caliber/issues/16) — check
   there before ordering, in case a pump is already being bought.

## What to order

### Option 1 — validate the SOP first (≈ $690)

Enough for ~25 samples, every grit re-orderable on its own, nothing committed in bulk before Gage
and Ronnie have run the SOP end to end.

| Line | Price |
| --- | ---: |
| OnPoint SiC 25-packs, 320/400/600/800/1200 | $214 |
| OnPoint FinalFloc 12″ PSA cloth, 10/pk | $95 |
| OnPoint Alumabrasive 1 µm alumina, 32 oz | $72 |
| OnPoint ProPrep 2 colloidal silica, 32 oz | $38 |
| Mark V black Bakelite, 5 lb | $40 |
| Ted Pella `16111` stubs, 100/pk | $34 |
| Ted Pella `16062-15` silver paint, 15 g | $58 |
| Parafilm `PM996` | $42 |
| Glass container sets ×3 (Chem Stores) | $75 |
| Vacuum gauge | $20 |
| **Total** | **≈ $688** |

Plus solvents and wash bottles from Chem Stores (~$150–200), which are a standing lab item rather
than a polishing-specific purchase.

### Option 2 — stock the lab for the year (≈ $1,600)

| Line | Price |
| --- | ---: |
| Mark V SiC, 100/box × five grits | $521 |
| OnPoint 12″ PSA cloth ×2 packs (one per alloy family) | $190 |
| 1 µm alumina, 32 oz ×2 | $144 |
| ProPrep 2 colloidal silica, 1 gal | $110 |
| Mark V black Bakelite, 5 lb | $40 |
| Ted Pella stubs, 500/pk | $165 |
| Ted Pella `16062` silver paint, 30 g | $158 |
| Parafilm `PM996` | $42 |
| Glass container sets ×3 | $75 |
| Vacuum gauge + 3 CFM two-stage pump | $160 |
| **Total** | **≈ $1,605** |

**Get an Allied quote in parallel either way.** Allied already supplies the alumina and the colloidal
silica on the shelf, so they are a known vendor to purchasing, and one PO covering `50-150-505`,
`90-187550` and `180-20000` may clear faster than three new vendors — even at a higher unit price.
Quote against the part numbers in the table at the top.

## Before any of it ships

1. **Measure a grinding disc, or the hold-down ring ID.** LECO prints 12″ as **305 mm**; Allied,
   OnPoint and PACE print it as **300 mm**. 12″ is 304.8 mm so at least one is a rounding
   convention, but a clamping ring is unforgiving. This is the only mistake here that wastes a whole
   box.
2. **Buy the 800 and 1200 papers from one brand.** Allied calls its 800 "P2400", Buehler calls its
   800 "P1500" — a real difference in abrasive size behind the same number.
3. **Write down what the two 1200 boxes actually say.** Standard vs Fine is a coating difference
   (sputter- vs electrostatically-coated), only LECO and Allied sell Fine, and the PSC's advice that
   standard 1200 suffices still stands for a first order.
4. **Check the alloy on each cloth before re-using it.** The SOP's own warning; it is also what makes
   the second cloth pack in Option 2 worth buying up front.

## Not priced here

- **Carbon conductive tabs** (Ted Pella `16084-1`) — quote-gated everywhere; ask for it on the same
  call as the stubs.
- **Diamond wafering blade** — still borrowed from the PSC, and the blade size is not recorded
  anywhere in the thread.
- **Metal pucks** — a machine-shop job, not a purchase.
- **Vibratory polisher** — the VibroMet 2 is discontinued and SOP §6 is still a stub, so there is
  nothing to specify against yet.
- **GreenLube / polishing lubricant** — an Allied bottle is visible on the shelf; Allied is
  quote-only and the SOP does not currently use lubricant with the alumina.

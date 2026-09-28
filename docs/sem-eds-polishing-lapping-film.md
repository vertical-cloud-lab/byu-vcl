# Finishing EDS samples on diamond lapping film instead of the 5 h silica polish

Written for [Ronnie's 2026-09-28 comment in #110](https://github.com/vertical-cloud-lab/byu-vcl/issues/110),
after he talked to Mike Standing at the BYU Electron Microscopy Facility (EMF). It checks what
Mike said and prices 1 µm, 0.5 µm and 0.1 µm abrasive film for the 12″ platen. Prices are list
prices read from the live product pages on 2026-09-28, before shipping and tax.

Step numbers refer to [Ronnie's Google Doc SOP](https://docs.google.com/document/d/1XJjOSDlwKRht6PhplwmZmqG202qoPPqnPQxjfCyigtU/edit):

| Step | What it is |
| --- | --- |
| 4 | SiC papers, 320 → 1200 |
| 5 | 1 µm alumina on the Imperial pad |
| 6 | Solvent and ultrasonic clean |
| 7 | VibroMet with colloidal silica, ~5 h |

## Short version

- **Mike is right that EDS doesn't need the EBSD-grade surface.** EDS-only samples can skip
  Step 7, the 5 h silica polish.
- **"1 µm or 0.5 µm is enough" is where the sources disagree with him, for aluminum.** Microprobe
  labs ask for about 0.1 µm for quantitative work:
  - Berkeley's EPMA lab asks for "a 1/10 micron diamond or 1/20 micron colloidal silica polished
    flat surface".
  - NIST's microprobe lab says aluminum "scratch[es] easily, requiring 0.1 µm to finish".

  So finish on **0.5 µm, then 0.1 µm** film. Each step takes minutes.
- **Below the 1200 paper (P4000, 2.5 µm), "sandpaper" is sold as lapping film:** abrasive bonded
  to a 3 mil polyester film.
- **Buy diamond film, not SiC film.** SiC is silicon, and fine SiC is known to embed in aluminum.
  Embedded diamond is carbon, which is never one of the quantified elements.
- **What to order:** [PACE](https://shop.metallographic.com) 12″ adhesive-back (PSA) diamond film,
  **$265 per pack of 3** for each grade. They stick to the platen the way the Imperial pad does.

## What Mike said, checked

| Mike said | Verdict | Evidence |
| --- | --- | --- |
| The ion mill only does a few square microns | **The conclusion holds, but that figure is the FIB's.** | The EMF lists the JEOL broad-beam mill as "Polishing can be targeted to approximately a 2mm area" ([EMF equipment](https://microscopy.byu.edu/ancillary-equipment), read 2026-09-26 through the CubXL Pi). The micron-scale tool is the EMF's Helios NanoLab 600 FIB: "The Gallium ion beam … can image and remove material down to 5nm resolution levels" ([EMF Helios page](https://web.archive.org/web/20250114195725/https://microscopy.byu.edu/helios-nanolab-600-fei)). Neither is a routine prep step for a stream of samples. |
| It contaminates the sample with the ion, e.g. Ar | **True, but small for the Ar mill.** The mill is off the table anyway. | Edison's 2026-09-26 review found the Ar-modified layer at 4–5 kV is "a few nanometres", and "no retrieved study documented a measurable EDS bias from Ar implantation on Al alloys" ([answer, assumption 5](https://github.com/vertical-cloud-lab/byu-vcl/blob/02e0e11/outputs/edison-rubber-duck-2026-09-26/rubber-duck-ion-mill-final-polish-plan-answer.md)). Ar Kα (2.96 keV) also misses the main lines of all 16 CALIBER elements. The FIB's gallium would matter more: Ga Lα (1.10 keV) sits 86 eV from Zn Lα (1.01 keV), the line Zn has to be measured on at 5 kV. |
| EDS doesn't need the very fine polish; that's for EBSD | **True for the silica step. The finish still needs to reach about 0.1 µm.** | EBSD signal comes from "a few 10's of nanometers deep", so the lattice there has to be undamaged ([Oxford Instruments text via UCR](https://cfamm.ucr.edu/sites/default/files/2019-09/Sample%20Prep-EBSD.pdf)). That is what the 5 h silica step is for, and EDS doesn't need it. But the microprobe sources still ask for 0.1 µm for quant ([Berkeley EPMA](https://pages.uoregon.edu/epmalab/UCB_EPMA/technical.htm); [Geller & Engle, NIST 2002](https://doi.org/10.6028/jres.107.051)). Rémond et al. (NIST 2002) add that leftover damage "may alter the accuracy … for elements present at trace levels or … at low incident energies or when soft x-ray photons are analyzed" ([doi](https://doi.org/10.6028/jres.107.052)). That describes our case: 5 kV, Mg at ~0.35 wt%, and O, Mg, Al and Si all measured on soft K lines. |
| A paper with 1 µm or ½ µm grit leaves much less behind than silica in a solution | **True for the residue we saw, with one exception: not SiC.** | The May residue was a layer of dried silica spheres. With colloidal silica, "a film can form on the polished surface of the sample which must be removed" ([ebsd.com](https://www.ebsd.com/hints-and-tips/ebsd-sample-preparation/polishing)). Film has no suspension to dry. Fixed abrasive also tends to embed less. Buehler says fine diamond embeds in aluminum "especially when suspensions are used" ([Buehler](https://www.buehler.com/blog/aluminum-metallographic-specimen-preparation-and-testing/)), and PACE says diamond film gives "less surface relief than diamond suspensions on cloth because the abrasive is fixed" ([PACE](https://www.metallographic.com/metallographic-technical/Metallography-Technical-Lapping-Films.htm)). No one has measured film-versus-suspension residue directly. **SiC is the wrong abrasive:** in aluminum, SiC embedding "usually arises with the finer grit size papers" ([Buehler Tech-Notes 3(2)](https://www.buehler.com/assets/solutions/technotes/vol3_issue2.pdf)), and each embedded grain reads as Si. |
| It saves a lot of time and removes the 5 h step | **True.** | PACE gives "30-90 seconds per micron of stock to remove" per film step. |

(Ronnie's comment says "Paul said" for the last three points. Paul was out, so these are read as
Mike's.)

## What to buy

### Recommended: PACE 12″ PSA diamond film

| Grade | Part # | Pack | Price | Per disc | Role |
| --- | --- | --- | ---: | ---: | --- |
| 0.5 µm | [`PDAA-05P12`](https://shop.metallographic.com/products/pdaa-05p12) | 3 | **$265** | $88 | new step after Step 5 |
| 0.1 µm | [`PDAA-01P12`](https://shop.metallographic.com/products/pdaa-01p12) | 3 | **$265** | $88 | final step, replaces Step 7 for EDS |
| 1 µm | [`PDAA-1P12`](https://shop.metallographic.com/products/pdaa-1p12) | 3 | $265 | $88 | optional; could later replace the Step 5 alumina |

- **$530 for the two that matter**, or $795 with the 1 µm.
- **All three show as available to order.**
- **The film is 12″, matching the platen.** The Imperial pad on the shelf is Allied `50-150-505`,
  "Adhesive Back Disc, 12″/300 mm", so PSA discs already go straight onto this platen.
- **Plain-back versions cost $225 per pack of 3:** [`PDA-05P12`](https://shop.metallographic.com/products/pda-05p12),
  [`PDA-01P12`](https://shop.metallographic.com/products/pda-01p12) and
  [`PDA-1P12`](https://shop.metallographic.com/products/pda-1p12). PACE says plain back gives
  "the best flatness and edge retention". The PSA adhesive "adds a small amount of compliance …
  [which] can cause edge rounding and relief on hard/soft interfaces". But plain back needs "a wet
  plate surface" to hold it, or the paper ring. PSA is the safer first order on a power head.
- **PACE sells two diamond lines at 12″, "Premium" (`PDAA-`) and standard (`DAA-`, $270).** The
  store doesn't say how they differ.

### Other sources

| What | Part # | Price | Notes |
| --- | --- | ---: | --- |
| Allied 12″ PSA diamond film, 1 / 0.5 / 0.1 µm | `50-30185` / `50-30190` / `50-30195` (5 per pack) | quote | [Allied](https://consumables.alliedhightech.com/Diamond-Lapping-Film-Discs-12-p/dlf12.htm). Allied already makes the alumina, silica and Imperial pad on the shelf, and its packs hold 5 discs, not 3, so ask for a quote alongside the PACE order. Allied says the film maintains "coplanarity regardless of varying materials or hardness within the sample". |
| Ted Pella PELCO **8″** PSA diamond, 1 / 0.5 / 0.1 µm | `814-462` / `814-461` / `814-460` | **$42.90 each** | [Ted Pella](https://www.tedpella.com/Material-Sciences_html/PELCO_Lapping_Discs.aspx). The cheapest way to try film, if the puck's path stays inside an 8″ (203 mm) disc (measure first), or by hand. |
| PACE 12″ PSA **alumina** film, 1 / 0.3 / 0.05 µm | [`ALO-1201PSA`](https://shop.metallographic.com/products/alo-1201psa-3) / [`ALO-12103PSA`](https://shop.metallographic.com/products/alo-12103psa-3) / [`ALO-12105PSA`](https://shop.metallographic.com/products/alo-12105psa-3) | $395 / $495 / $495 per 100 | The fallback if the SEM shows embedded diamond (see below). There is no 0.5 µm or 0.1 µm grade. |

**Not SiC.** The finest 12″ SiC *paper* is the 1200 you already use, which is P4000, 2.5 µm
([PACE chart](https://www.metallographic.com/Brochures/SiCpaper.pdf)). 1 µm SiC exists only as
film. It adds Si, and fine SiC is the grade that embeds in aluminum.

## Why diamond, and the one argument for alumina

Residue from each abrasive adds a different element:

| Abrasive | What its residue adds | Effect on our quant |
| --- | --- | --- |
| silica | Si, O | **Si is an analyte.** This is the May problem. |
| SiC | Si, C | **Si is an analyte.** |
| alumina | Al, O | Al is the base metal, so it only dilutes Si and Mg slightly and adds O ([09-25 estimate](https://github.com/vertical-cloud-lab/byu-vcl/blob/2e5dc74/docs/sem-eds-polishing-silicon-free-final-polish.md#2-how-much-each-residue-shifts-the-eds-result)). |
| diamond | C | C is never quantified. NIST: "Embedded diamond in a sample is relatively easy to recognize and does not interfere with most analytical jobs" ([Geller & Engle](https://doi.org/10.6028/jres.107.051)). |

**The case for alumina film instead.** PACE recommends alumina film "for soft or ductile metals
where diamond would embed". Against it:

- **It is a poor fit for our power head.** Allied says its alumina film is "not recommended for
  power head applications" ([Allied](https://consumables.alliedhightech.com/Aluminum-Oxide-Lapping-Films-p/aloflm.htm)).
- **The grades jump from 1 µm to 0.3 µm to 0.05 µm,** with nothing at 0.5 µm or 0.1 µm.
- **It only comes in 100-packs,** $395–495 per grade.

So start with diamond, and **look for embedded diamond at the SEM.** Embedded diamonds show up as
dark specks in BSE. If there are many, switch the last step to alumina film.

## Running film on our machine

- **Start clean.** Clean and dry the platen before sticking film down. A grain under a 3 mil film
  prints through as a bump.
- **Lubricate with water.** PACE: "Maintain adequate lubricant flow to prevent swarf buildup and
  film damage."
- **Go slower and lighter than on the papers:**
  - Speed: "60-120 RPM for fine films (≤9 µm)", "head and platen in the same direction at matched
    speeds".
  - Force: "2-5 lbs per specimen (≈9-22 N per specimen)".
  - The SOP's "gentle" setting runs the platen at 150, above that range. Try about 100, with the
    lowest force setting.
- **Time each step by what it has to remove.** PACE: "30-90 seconds per micron of stock to
  remove." Move on when the previous step's scratches are gone under the optical microscope, the
  same rule as the papers. "Clean specimen and film for the final 10-15 seconds of the polishing
  cycle."
- **Rinse the puck, holder and platen between grades**, exactly as between papers.
- **Store film like the pads:** liner back on the adhesive, bagged and labeled with the alloy. Film
  is reused until it shows "reduced cutting efficiency", "visible wear patterns or bald spots", or
  swarf "that won't rinse away" (PACE).
- **Then clean as in Step 6.** The 2 min water polish from the 09-26 write-up is only needed after
  silica.

## Suggested first run

Two pucks from the same build, plus the pure Al pellet with puck B:

| Puck | Steps |
| --- | --- |
| A | Step 4 → Step 5 (1 µm alumina) → Step 6. No film, no Step 7. |
| B + Al pellet | Step 4 → Step 5 → **0.5 µm film → 0.1 µm film** → Step 6 |

Compare them at the SEM in one session:

1. **SE and BSE at ≥ 50,000×**, for scratches, residue and embedded diamond.
2. **EDS at 5 kV** for Si, O and C, in three areas per puck. Keep C in the element list.
3. **The pellet is a built-in blank.** Pure Al has no Si, so any Si it shows is contamination.
4. **Repeat one area at 15 kV.** Rémond's data suggest the finish matters much less there: on
   alumina ceramic, diamond- versus silica-polished Al Kα differed by 14–24% at 5 keV but ≤2% at
   15 keV ([Table 6](https://doi.org/10.6028/jres.107.052)). That is a ceramic, which traps
   charge, so the effect in a metal should be smaller.

If B is clean, it becomes the EDS finish. If A is already as good, the film can be kept for 5 kV
work only.

## What this changes from earlier write-ups

- **The ion mill is out.** That undoes the 09-25 and 09-26 recommendations built on it.
- **Silica is now only for EBSD samples.** The ProPrep 2 in [order 13380](https://meorders.byu.edu/order/13380)
  is only needed if EBSD is planned. The same goes for the 2 min water polish.
- **The VibroMet alumina trial in the [09-25 write-up](https://github.com/vertical-cloud-lab/byu-vcl/blob/2e5dc74/docs/sem-eds-polishing-silicon-free-final-polish.md#6-suggested-next-run)
  is no longer needed for EDS.**

## Sources

- Geller & Engle, "Sample Preparation for Electron Probe Microanalysis—Pushing the Limits",
  *J. Res. NIST* 107 (2002) 627, [doi:10.6028/jres.107.051](https://doi.org/10.6028/jres.107.051):
  "Aluminum and copper: these metals scratch easily, requiring 0.1 µm to finish"; diamond paste,
  no oxide abrasives.
- Rémond, Nockolds, Phillips & Roques-Carmes, "Implications of Polishing Techniques in Quantitative
  X-Ray Microanalysis", *J. Res. NIST* 107 (2002) 639, [doi:10.6028/jres.107.052](https://doi.org/10.6028/jres.107.052):
  bound (two-body) vs loose (three-body) abrasive, low-kV sensitivity, Table 6.
- UC Berkeley EPMA lab, [technical notes: sample preparation](https://pages.uoregon.edu/epmalab/UCB_EPMA/technical.htm).
- Oxford Instruments, "Sample Preparation for EBSD", via [UCR CFAMM](https://cfamm.ucr.edu/sites/default/files/2019-09/Sample%20Prep-EBSD.pdf).
- PACE Technologies, [*Lapping Films*](https://www.metallographic.com/metallographic-technical/Metallography-Technical-Lapping-Films.htm)
  (abrasive choice, backing, speed, force, step time, replacement) and
  [SiC paper grit chart](https://www.metallographic.com/Brochures/SiCpaper.pdf).
- Buehler, [aluminum preparation guide](https://www.buehler.com/blog/aluminum-metallographic-specimen-preparation-and-testing/)
  and [*Tech-Notes* 3(2)](https://www.buehler.com/assets/solutions/technotes/vol3_issue2.pdf).
- Allied High Tech, [12″ diamond lapping film](https://consumables.alliedhightech.com/Diamond-Lapping-Film-Discs-12-p/dlf12.htm)
  and [aluminum oxide lapping film](https://consumables.alliedhightech.com/Aluminum-Oxide-Lapping-Films-p/aloflm.htm).
- EBSD.com, [polishing hints](https://www.ebsd.com/hints-and-tips/ebsd-sample-preparation/polishing).
- BYU EMF, [ancillary equipment](https://microscopy.byu.edu/ancillary-equipment) and
  [Helios NanoLab 600](https://web.archive.org/web/20250114195725/https://microscopy.byu.edu/helios-nanolab-600-fei) (Wayback, 2025).

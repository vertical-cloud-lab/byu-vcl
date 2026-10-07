# McMaster-Carr and stock-material alternatives for Si, Fe, Ni, Cu (2026-10-06)

Issue #161. The Thermo Fisher order (ME order 13300) was never placed and quote #M6449
has expired. It covered four lines:

| Line | Thermo part | Spec | Pack | Quoted |
| --- | --- | --- | --- | ---: |
| Si | 000311-22 | −100 mesh, 99.9% | 100 g | $106.00 |
| Fe | 047355-30 | −20 mesh, 99.9% | 250 g | $122.00 |
| Ni | 010579-22 | −60+170 mesh, 99.7% | 100 g | $68.90 |
| Cu | 042623-22 | spherical −100+325 mesh, 99.9% | 100 g | $57.80 |

What the 20-run campaign actually consumes, from
[`purchase_quantity_model.py`](purchase_quantity_model.py) with its 1.25× contingency:
**Si ~30 g, Cu ~20 g, Ni ~5 g, Fe ~2.5 g.**

## What McMaster has

Read 2026-10-06 from the Pi 5 stream cam's headless Chromium (`docs/pi-tooling.md` on
the issue-222 branches). Prices are McMaster web prices, not BYU punch-out prices.

**Metal powders.** One family, *Additives and Fillers for Paints, Coatings, and
Lubricants*, all 1 lb plastic bottles:

| Element | Part | Purity ("concentration") | Particle size | Price |
| --- | --- | --- | ---: | ---: |
| Cu | [1402N18](https://www.mcmaster.com/1402N18/) | 99.9% | 44 µm | $90.72 |
| Fe | [1402N25](https://www.mcmaster.com/1402N25/) | 99.9% | 5 µm | $85.50 |
| Ni | [1402N24](https://www.mcmaster.com/1402N24/) | 99.9% | 3 µm | $143.22 |
| Si | — | none stocked: a "silicon" search returns silicone and silicon carbide only | | |

Same family, for reference against the ESPI order: Al 99.9% 44 µm `1402N19` $73.08,
Mn 97% 10 µm `1402N26` $190.00, Sn 99.9% 44 µm `1402N16` $142.50. None of these beats the
ESPI quote, and McMaster has no Cr, Zn, Ti or Mg metal powder at all.

No material certificate is listed for this family. McMaster's metal 3D-printer powders
and raw-material bar stock do come with lot certificates, so the 99.9% here is the label's
word only, and its basis (metals or total) is not stated.

**Bar and wire stock.**

| Element | What McMaster stocks |
| --- | --- |
| Ni | *Corrosion-Resistant 200 Nickel Rods*, ASTM B160 (Nickel 200 is ≥ 99.0% Ni by that spec; McMaster's page says "over 98% pure"), lot certificate downloadable after shipping: [9136K23](https://www.mcmaster.com/9136K23/) Ø1/2" ±0.002", $75.62 per 1/2 ft; [9136K25](https://www.mcmaster.com/9136K25/) Ø3/4", $109.42 per 1/2 ft |
| Cu | Raw Materials › Copper: 186 rod and 99 wire products, all with material certificates (alloy grades not pulled) |
| Fe | Nothing. An "iron wire" search returns only welding and brazing products |
| Si | Nothing |

## Do the McMaster powders work for us?

**Purity matters little at these loadings.** Using the quote review's measure (max wt.%
in the alloy × (1 − purity)): Cu at 4 wt.%, Ni at 2 wt.% and Fe at 1 wt.% give 40, 20 and
10 ppm of tramp elements at 99.9%. Even if the true purity were 99.0%, that is 400, 200 and
100 ppm, still small next to the 2,715 ppm the 99.7% Al base contributes.
*(2026-10-07: this only holds for a 99.7% base. With a 4N or 5N rod the solutes dominate. See
[`al-ni-purity-and-industry-feedstock-2026-10.md`](al-ni-purity-and-industry-feedstock-2026-10.md) §3.)*

**They are far too fine for the augers.** The cohesion index (250 µm / d)² is 32× for Cu,
2,500× for Fe and 6,900× for Ni, against ~10× as the point where powder stops feeding.
That only matters for Cu: the campaign uses 5 g of Ni and 2.5 g of Fe in total, which get
weighed into the cups by hand in the glovebox anyway.

*(2026-10-07: Ni is not slow. Liquid Al holds 17.7 wt% Ni at 750 °C against 4.1 wt% Fe, so Ni
dissolves ~4× faster than Fe; see the Al–Ni doc §2.)*

**Fine is good for dissolving, but 3–5 µm powder sinters.** Fe and Ni dissolve slowly, so
fine particles help, as the September Edison corroboration found. Bartosz's warning from
the 9/17 call applies here, though: loose fine powder can sinter into a cake before any
liquid reaches it. Mix the Fe and Ni into the other powder in the cup instead of packing
them as their own layer.

**Handle Ni and Fe in the glovebox only.** At 3 µm, the Ni is respirable, and nickel metal
is a suspected carcinogen (GHS Carc. 2) and a skin sensitiser. The 5 µm Fe is a combustible
dust and can self-heat. The 44 µm Cu is low hazard.

## Atomizing stock ourselves

| Element | Melting point | Pure element on the induction module (1300 °C rated) |
| --- | ---: | --- |
| Cu | 1085 °C | Possible, but a full atomizer run (and the crucible and sonotrode exposure) to make ~20 g of powder that costs $91 |
| Si | 1414 °C | Above the rating |
| Ni | 1455 °C | Above the rating |
| Fe | 1538 °C | Above the rating |

Atomizing them into powder isn't necessary, though. As with Ti
([`al-ti-melt-window.md`](al-ti-melt-window.md)), stock goes straight into the Al charge
and dissolves in liquid Al far below its own melting point:

- **Ni:** the Ø1/2" Ni 200 rod (9136K23) sliced 1 mm thick gives discs of about 1.1 g that
  fit the cups' 1/2" bore. That is two discs for a 2 wt.% Ni run. A 6" length (~172 g) is
  far more than the campaign needs. Keep the slices thin and check the first run by
  sectioning or ICP: Bartosz's other warning was that a small high-melting addition can
  sit in one spot.
- **Cu:** copper wire or rod cut to weight. Cu dissolves readily into Al, since the Al–Cu
  eutectic is 548 °C.
- **Si:** Al 4047 (Al–12Si), the alloy of Bartosz's benchmark rods, is already the
  composition of the Al-Si-Mg-Cu family (Si ≤ 12 wt.% in the model). A cup machined from
  4047 brings the Si with it. 4047 allows up to 0.8% Fe, so get its certificate. Higher-
  purity routes are ESPI's Al-Si 4N/5N pieces
  ([`master-alloy-ingot-sourcing-2026-09.md`](master-alloy-ingot-sourcing-2026-09.md)) or
  Si powder from AEE, below.
- **Fe:** McMaster turned up no pure-iron stock. The 1402N25 powder or a Thermo re-quote covers
  the 2.5 g.
- **Fallback:** if a cup run shows undissolved Fe or Ni, arc-melt Al-Fe and Al-Ni masters
  first (#223).

## Silicon, since McMaster has none

Atlantic Equipment Engineers (Micron Metals) is already quoting the AL-111 aluminium. The
repo's `silicon-powder-mcmaster-carr-sds…pdf` is AEE's SI-100/101 sheet, so McMaster appears
to have resold AEE silicon at some point; it does not list any now. From
[micronmetals.com](https://micronmetals.com/product/silicon-powder-2), 100 g minimum:

| Catalog | Purity | Size | Price |
| --- | --- | --- | --- |
| SI-111 | 99.99% | 45–90 µm | not listed |
| SI-122 | 99.999% | −100+325 mesh (45–150 µm) | not listed |
| SI-113-F | 99.9+% | 15–53 µm | $156.39/lb (1–2 lb) |
| SI-101 | 99+% | −325 mesh | not listed |

## Options

| Option | Covers | Cost | Notes |
| --- | --- | ---: | --- |
| A. McMaster today: 1402N18 + 1402N24 + 1402N25 | Cu, Ni, Fe | $319.44 | Same three lines were $248.70 at Thermo. Ships fast on BYU's McMaster account; far finer than the Thermo cuts |
| A′. Same, with the Ni 200 rod (9136K23) instead of 3 µm Ni | Cu, Ni, Fe | $251.84 | Certified, no respirable Ni; Ni added as slices |
| B. Ask Thermo to re-issue #M6449 | Si, Fe, Ni, Cu | $354.70 | Coarser cuts, closer to 150–300 µm. Si was ETA, not stock |
| Si: AEE (add to the AL-111 order) or 4047 cups | Si | ≤ $156 (SI-113-F, 1 lb) | Others quote-only; see above |

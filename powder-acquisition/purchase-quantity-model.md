# Purchase-Quantity Model — First Round: 20 × 100 g Atomizer Runs

**Context:** [Issue #161 — Atomizer Powder Acquisition](https://github.com/vertical-cloud-lab/byu-vcl/issues/161). This model sizes the first feedstock purchase for **20 ultrasonic-atomization runs at 100 g each (2.0 kg total charge)**, using the purity and form decisions already settled in [purity-and-particle-size-recommendations.md](purity-and-particle-size-recommendations.md):

- Al, Zr, Er, Sc, Mg → **99.99%** basis
- Mn, Cr, Si, Cu, Zn, Ti, Ni, Fe, Sn, Ce → **99.9%**
- Li → **Al–Li master alloy only** (elemental Li powder is pyrophoric)

A companion script, [`purchase_quantity_model.py`](purchase_quantity_model.py), recomputes every number in this document from the assumption tables below — edit the assumptions there and re-run as the campaign plan firms up.

## 1. Campaign allocation (the adjustable knob)

The model assumes the 20 runs split across the focus chemistries from the PR #88 shopping-list discussion (Al–Mn–Cr–Zr / Al–Zr first), plus exploratory families. **Every run is priced at the worst case — the maximum wt.% of each element in its family** — so real consumption will come in under these numbers.

| Family | Runs | Max solute levels assumed (wt.%) |
| --- | ---: | --- |
| Al–Mn–Cr–Zr (+Ti grain refiner) | 8 | Mn 5, Cr 2, Zr 2, Ti 0.5 |
| Al–Zr–Er–Sc microalloyed | 4 | Zr 1.5, Er 1, Sc 0.8, Ti 0.5 |
| Al–Ce–Mg | 3 | Ce 10, Mg 6 |
| Al–Si–Mg–Cu | 2 | Si 12, Mg 0.5, Cu 4, Fe 1, Sn 1 |
| Al–Zn–Mg–Cu (7xxx-like) | 2 | Zn 8, Mg 3, Cu 2, Ni 2 |
| Al–Li–Cu exploratory | 1 | Li 2, Cu 4 |

## 2. The formula

For each element:

```
element need (g) = Σ over runs [ 100 g × max wt.% ]
                   × volatility over-charge (1.15 for Mg, Zn, Li; 1.10 for Mn; 1.00 otherwise)
                   × 1.25 contingency (spillage, weighing losses, one re-run)
```

For elements bought as master alloys, divide by the master-alloy solute fraction to get the master-alloy mass. The over-charge factors come straight from the Edison literature findings (5–15% evaporation loss for volatile elements on rePowder-type systems).

## 3. Element requirements and buy list

| Element | Charged, worst case (g) | After over-charge + 25% contingency (g) | Purchase form | **Buy quantity** |
| --- | ---: | ---: | --- | --- |
| **Al** (base) | 1788 | ~1428 elemental (rest arrives inside master alloys) | 99.99% (4N) **shot/granules**, not fine powder | **2 × 1 kg** |
| Mn | 40.0 | 55.0 | 99.9% electrolytic flake/coarse powder | **100 g** |
| Cr | 16.0 | 20.0 | 99.9% coarse powder/granules | **50–100 g** (min pack) |
| Zr | 22.0 | 27.5 → **275 g of Al-10Zr** | **Al-10Zr master alloy** (4N Al base, see §5) | **300 g** |
| Mg | 25.0 | 35.9 | 99.99% granules/turnings — **not fine powder** | **100 g** |
| Si | 24.0 | 30.0 | 99.9% lump/coarse granules | **100 g** |
| Cu | 16.0 | 20.0 | 99.9% shot/granules | **50–100 g** |
| Zn | 16.0 | 23.0 | 99.9% shot/granules | **50 g** |
| Ce | 30.0 | 37.5 → **188 g of Al-20Ce** | **Al-20Ce master alloy** (or Al-10Ce × 375 g) | **250 g** |
| Ti | 6.0 | 7.5 → **150 g of Al-5Ti-1B** | **Al-5Ti-1B rod** (commodity grain refiner) | **200 g** |
| Er | 4.0 | 5.0 → **50 g of Al-10Er** | **Al-10Er master alloy** (low-O, see §5) | **100 g** (typical min pack) |
| Sc | 3.2 | 4.0 → **200 g of Al-2Sc** | **Al-2Sc master alloy** (industry standard) | **250 g** |
| Ni | 4.0 | 5.0 | 99.9% granules | **25–50 g** |
| Fe | 2.0 | 2.5 | 99.9% granules/coarse powder | **25–50 g** |
| Sn | 2.0 | 2.5 | 99.9% shot | **25–50 g** |
| Li | 2.0 | 2.9 → **29 g of Al-10Li** | **Al-10Li (or Al-5Li × 58 g) master alloy — never elemental** | **smallest pack (50–100 g)** |

**Al balance check:** worst-case solute across 20 runs = 212 g, so ~1788 g of Al is charged in total. The master alloys above deliver ~646 g of that Al; the remaining ~1142 g comes from elemental 4N shot, which lands at ~1428 g after the 1.25 contingency factor. **2 kg of 4N Al shot** covers this plus practice melts.

## 4. Rough cost envelope (planning-grade only — get quotes)

These are order-of-magnitude planning ranges from July 2026 list-price research earlier in issue #161; several items (master alloys especially) are quote-only. Per @sgbaird's suggestion, calls to MSE Supplies / American Elements / KBM Affilips (master alloys) should replace these before ordering.

| Block | Est. range |
| --- | --- |
| 4N Al shot, 2 kg | $300–800 |
| Mn, Cr, Si, Cu, Zn, Ni, Fe, Sn (eight 25–100 g packs, 99.9%) | $250–700 |
| Mg 99.99% granules, 100 g | $50–150 |
| Al-10Zr 300 g + Al-5Ti-1B 200 g | $150–350 |
| Al-2Sc 250 g + Al-10Er 100 g + Al-20Ce 250 g | $400–1,000 |
| Al-Li master, 50–100 g | $150–400 |
| **Total (no hazmat surcharges expected — no class 4.2 items in this list)** | **~$1,300–3,400** |

Buying Zr and Li as master alloys removes both anticipated dangerous-goods surcharges (~$100–300 each) from the earlier elemental-powder plan.

## 5. Purity caveat for the 99.99% elements bought as master alloys

Zr, Er, Sc are on the 99.99% list but arrive as master alloys, where a single "99.99%" label doesn't apply. What actually protects the L1₂-precipitation chemistry is:

1. **4N Al base** in the master alloy (ask the supplier explicitly), and
2. **low oxygen/oxide content** — request the certificate of analysis with O, Fe, Si reported.

A master alloy made from 4N Al and 99.9%+ solute is metallurgically equivalent to (and lower-oxide than) blending 4N elemental powders, because the solute is already dissolved and its surface oxide is gone.

## 6. What this model does *not* cover

- Sonotrode-contamination allowance (Mo/Ti pickup) — plan ICP/EDS on the first atomized batches.
- Sieve-yield losses downstream of atomization (this buys *melt feedstock*, not finished 15–45 µm LPBF powder).
- Auger/feed-system hold-up volume — pending @swcharles's answer on auger capacity in issue #161.

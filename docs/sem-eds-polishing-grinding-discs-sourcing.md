# SiC grinding discs for the rotary polisher — sourcing

Where to buy the 320 → 1200 silicon-carbide papers called for in step 4 of the SEM/EDS polishing
SOP ([issue #110](https://github.com/vertical-cloud-lab/byu-vcl/issues/110)), and what they cost.

> **Prices are vendor list prices captured 2026-09-23**, before shipping and tax, for the US sites.
> Allied High Tech and LECO publish no online prices — those two need a phone/email quote.

## The spec is not a guess

It is read off the boxes in
[Gage's shelf photo](https://github.com/vertical-cloud-lab/byu-vcl/issues/110#issue-4471024294):
**12″ dia (305 mm), plain back, silicon carbide, wet or dry, 100/box.** Plain back — *not* PSA — is
what the SOP's "metal sand paper holding ring" clamps. One of those boxes is hand-labelled
"Fullwood On[ly]", which is the reason for buying our own.

| Grit | LECO part # (what's on the shelf) | Allied equivalent | Notes |
| --- | --- | --- | --- |
| 320 | `810-295-PRM` | `50-10165` — 320 (P400) | |
| 400 | `810-296-PRM` | `50-10170` — 400 (P800) | |
| 600 | `810-297-PRM` | `50-10175` — 600 (P1200) | |
| 800 | `810-856-100` | `50-10176` — 800 (P2400) | |
| 1200 | `810-857-100` | `50-10177` — 1200 (P4000) | |
| 1200 **fine** | `810-857-500` | `50-10178` — 1200 (Fine) | separate product, see below |

All LECO boxes are 100/pkg; all Allied are Pk/100.

## Price comparison — 12″ plain back, 100/box

| Vendor | 320 | 400 | 600 | 800 | 1200 | **One box of each** | $/disc (coarse / fine) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **[Mark V Lab](https://www.markvlab.com/replacement-leco-supplies/category/132-silicon-carbide-grinding-discs-plain-back)** (LECO replacement) | $87 | $87 | $87 | $130 | $130 | **$521** | **$0.87 / $1.30** |
| [OnPoint Abrasives](https://onpointabrasives.com/collections/metallographic-sic-grinding-paper) CarbiPro | $124 | $124 | $124 | $179 | $179 | $730 | $1.24 / $1.79 |
| [Beta Diamond](https://betadiamond.com/products/silicon-carbide-grinding-paper-12-inch) | $130 | $130 | $130 | $178 | $178 | $746 | $1.30 / $1.78 |
| [PACE Technologies](https://shop.metallographic.com/collections/silicon-carbide-sic-grinding-papers) | $170 | $170 | $170 | $300 | $300 | $1,110 | $1.70 / $3.00 |
| Buehler CarbiMet / MicroCut ([JH Technologies](https://shop.jhtechnologies.com/collections/silicon-carbide-paper/buehler)) | $201 | $201 | $201 | $440 | $440 | $1,483 | $2.01 / $4.40 |
| Allied High Tech | — | — | — | — | — | quote | quote |
| LECO (OEM) | — | — | — | — | — | quote | quote |

At one disc per grit per sample (the SOP treats all papers as single use), **a box of 100 is roughly
100 samples' worth**. The 800 and 1200 papers cost noticeably more than 320–600 everywhere, because
the fine grades are slurry/sputter coated rather than electrostatically coated.

### Smaller first order

500 discs is a lot of paper to commit to before the SOP has been run end to end.

| Option | Contents | Price |
| --- | --- | --- |
| [OnPoint 25/pkg](https://onpointabrasives.com/collections/metallographic-sic-grinding-paper) | 25 each of 320, 400, 600 @ $38 + 800, 1200 @ $50 | **$214** (≈25 samples) |
| Allied `ASSORT-P/B12` | 25 each of 180, 320, 600, 1200 — one part number | quote (no 400 or 800) |

OnPoint's 25-packs work out to $1.52/disc coarse and $2.00/disc fine — a ~25–50% premium over their
own 100-box, but a quarter of the upfront spend, and each grit is re-orderable independently.

### Don't buy PSA

PSA (adhesive-back) discs are the wrong backing for a ring-clamped platen *and* cost about twice as
much: Mark V is $172 vs $87 for 12″ 400/600 grit, PACE $240 vs $170, OnPoint $190 vs $124.

## Three things to check before the order goes in

1. **Diameter — the one that can waste the whole order.** LECO prints its 12″ discs as **305 mm**;
   Allied, OnPoint and PACE print theirs as **300 mm** (12″ is 304.8 mm, so at least one of those is
   a rounding convention rather than a real 5 mm difference). Beta Diamond states 305 mm explicitly.
   A hold-down ring is unforgiving about this, so measure a disc out of the existing Fullwood box —
   or the ring's inner diameter — and ask the vendor for the *actual* diameter, not the nominal one.
2. **The fine-grit numbering is not standardized across brands.** Allied labels its 800 "P2400";
   Buehler labels its 800 "P1500". Allied's 1200 is "P4000"; Buehler's 1200 is "P2500", with P4000
   sold as a separate item. The 320/400/600 steps agree everywhere (P400/P800/P1200), but **buy the
   800 and 1200 from a single brand** so the step sizes are consistent.
3. **New-vendor setup.** Allied is already a supplier to this workflow (the 1 µm alumina and the
   0.05 µm colloidal silica are theirs), so an Allied order may clear purchasing fastest even at a
   higher unit price. Mark V Lab, OnPoint and Beta Diamond would be new vendors on
   [meorders.byu.edu](https://meorders.byu.edu).

## "1200 plain vs 1200 fine" — answered

This was left open in the SOP thread. It is a **real two-product distinction in both the LECO and
Allied catalogs**, not a texture variation, and Allied states the difference plainly:

> Fine grit papers are **electrostatically coated**, allowing continued stock removal (cutting)
> after the 600 grit step. They differ from standard 800/2400 and 1200/4000 grit discs, which are
> **sputter coated** and "polish" more than "cut."
>
> — [Allied, Silicon Carbide Fine Grit Discs](https://consumables.alliedhightech.com/Silicon-Carbide-Fine-Grit-Discs-p/sicfg.htm)

Allied's stated use case for the fine line is "pre-diamond polishing, **softer materials that
smear**, or step grinding for failure analysis." Aluminum is a soft material that smears, so this is
worth a trial box eventually — but the PSC staff's advice that standard 1200 is sufficient stands
for the first order. Only LECO and Allied sell it; Mark V, OnPoint, Beta Diamond, PACE and Buehler
do not offer a "Fine" variant at all.

Allied's fine-grit line has its own part numbers, separate from `50-101xx`: 12″ discs are
`53-10180` (1000), `53-10181` (1200), `53-10182` (1500), `53-10184` (2500), sold **250 per package**.

## Recommendation

- **Default: Mark V Lab, $521** for 100 each of 320/400/600/800/1200. It is the cheapest by a wide
  margin, and it is explicitly sold as a LECO replacement — the same thing the lab already runs.
- **Lower-commitment: OnPoint 25-packs, $214** for 25 of each of the five grits, if we'd rather
  validate the SOP before buying 500 discs.
- **Get an Allied quote in parallel** using the part numbers above. If it lands anywhere near Mark V,
  the procurement convenience probably wins.

Not covered here: the polishing pads, the 1 µm alumina suspension, and the 0.05 µm colloidal silica
— those are separate line items in the SOP's consumables.

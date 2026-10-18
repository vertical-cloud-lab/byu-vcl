# 2026-10-18 — which opaque 96-well plate to buy (no motion)

Asked on [PR #202](https://github.com/vertical-cloud-lab/byu-vcl/pull/202) by @sgbaird, quoting the
10-14 fix ("an opaque (black-walled) 96-well plate, or white and black wells right next to each
paint"): "Look up specific products that you'd recommend getting, use the raspberry Pi".
Prices were read on 2026-10-17, 22:30–22:45 MDT. Nothing on the robot or the Pi changed.

## Recommendation: Corning 3915

96-well, **solid black**, flat bottom, polystyrene, not treated, nonsterile, no lid, 360 µL wells
(Corning's product page: "Plate Color Black · Well Bottom Flat · Well Volume 360 µL · Surface
Treatment Not Treated · Sterile No · Lids Included No").

| seller | what | price | stock |
| --- | --- | --- | --- |
| [Antibodies Inc.](https://antibodiesinc.com/products/costar-96-well-black-polystyrene-plate-266) (ImmunoChemistry Technologies, SKU 266) | **1 plate** | **$8.45** | "Ships: 1-2 business days" |
| [Government Scientific Source](https://www.govsci.com/product-detail/Corning/3915/CS/) | case of 100 (4 × 25) | $476.00 | "In Stock: 11 left" |
| [Capitol Scientific](https://www.capitolscientific.com/Corning-3915-96-Well-x-360L-Flat-Bottom-Assay-Microplate-without-Lid-Non-Treated-Black-Polysty) (COR-3915) | case of 100 | $445.12 | lead time on request |
| [Weber Scientific](https://www.weberscientific.com/costar-96-well-black-and-white-solid-plates) (COS3915) | case of 100 | $435.23 | "On Order" |
| [Corning](https://ecatalog.corning.com/life-sciences/b2c/US/en/p/3915), direct, credit card at list | case of 100 | $469.15 | "In Stock", but "Estimated Shipment Date Jan 31, 2027" |
| Fisher Scientific, 07-200-590 | case of 100 | not read | |

- **Buy 3–5 single plates first.** The single plate is the same Corning 3915: Biomol lists the
  same ICT item as "Costar(R) 96-Well Black Polystyrene Plate (no. 3915)", "black polystyrene,
  untreated, flat bottom, … non-sterile", "sold individually"
  ([Biomol](https://biomol.com/products/toolkits/kit-components/costar-r-96-well-black-polystyrene-plate-no.-3915-ict-266)).
  The Antibodies Inc. page itself doesn't print the Corning number.
- **If it works, a case of 100** from Government Scientific Source, the only case seller that showed
  stock.
- **Fisher:** its search for "corning 3915" returned 07-200-590, *Corning 96-Well Solid Black or White
  Polystyrene Microplates*. Its product page refused the Pi, so no price was read.

### Why this one

- **The robot already knows it.** Opentrons' stock `corning_96_wellplate_360ul_flat` (versions 1–3; the
  definition [`tip_cal.py`](tip_cal.py) and [`protocols/02_read_height_over_well.py`](protocols/02_read_height_over_well.py) load) lists 3915 among its `brandId`s, and its `links` entry is
  Corning's *96-well Solid Black and White Polystyrene Microplates* page. Corning's dimension drawing
  ([MicroplateDimensions96-384-1536.pdf](https://www.corning.com/catalog/cls/documents/drawings/MicroplateDimensions96-384-1536.pdf),
  sha256 `fe6819af…f225`) puts 3915 in the same row as the clear 3370: 360 µL, well depth 10.67 mm,
  well Ø 6.86/6.35 mm, 127.8 × 85.5 × 14.2 mm, A1 offsets 11.2 / 14.3 mm, well bottom 3.55 mm up. Those
  are the definition's numbers (14.22 mm tall, 10.67 mm deep, well bottom at z 3.55, A1 at
  14.38, 74.24). So slot 7, the H-row positions and z 92 carry over unchanged.
- **Black has the least cross-talk.** Revvity: "Clear plates can have the highest cross talk, with
  black plates having the lowest. White plates give medium cross-talk"
  ([`accuracy-sources-2026-10-02.md`](accuracy-sources-2026-10-02.md)).
- **A solid bottom stops the light from below.** On the clear plate an empty well's light comes largely
  up through the plastic, which is why the empty-well subtraction failed and why empty wells read
  0.03 (F3) to 0.61 (F12) on the white/black scale
  ([`results-background-subtraction-2026-10-14.md`](results-background-subtraction-2026-10-14.md)). With
  nothing coming up through the plate, the paper under it no longer matters.
- **Not treated and nonsterile is the cheapest version.** Neither matters for paint.

### Not recommended

- **3912, solid white** ($453.11 per 100 at Weber, "On Order"; $476.54 at Corning). Same geometry, but
  white walls give medium cross-talk.
- **3631, black walls with a clear bottom** ($736.45 per 100 at Corning, "Estimated Shipment Date Jan
  26, 2027"). Corning's drawing gives it the same well positions and depth as 3915, with a 0.5 mm bottom
  instead of 1.27 mm, though it isn't in Opentrons' list. Light still comes up through the bottom, so
  it's only worth it with a light panel under the plate (the AC's 2026 method, §1b of
  [`accuracy-provenance.md`](accuracy-provenance.md)).
- **Generic black plates** (Amazon and others): their heights and well depths aren't published, and the
  read height depends on the plate's height.
- **For the other fix, white and black wells beside each paint, there's nothing to buy.** The Titanium
  White and Mars Black are on hand (in H12 and H7 since 09-30, refilled undiluted on 10-06).

## What to expect

- **Dimmer readings.** Today some of the light reaching the paint comes up through the plate. On a solid
  black plate it only comes in from above, through the gap under the foot. There's room: the readings use
  2–4% of the sensor's range, and gain and integration time are settable per reading since 10-10.
- **Untested.** First run on it: the same five paints plus a few empty wells, read at z 92. Then compare
  points off with 10-06 (12.2) and 10-14 (17.8), and check whether empty wells still change from F3 to F12.

## How the prices were read

From the Pi behind `RPI_STREAM_CAM_HOSTNAME` (idle, load 0.06), because these sites refuse CI runners.
Nothing was written on the Pi.

- **`curl` on the Pi, capped at 400 KB/s:** Corning's catalogue (the family page listing 22 solid
  black/white plates, and the 3915 and 3631 product pages), the drawing PDF, Antibodies Inc. (Shopify's
  product `.js`, then the page), Weber, Capitol and Government Scientific Source. Fisher and Sigma-Aldrich
  answered `curl` with "Access Denied", and Amazon with a JavaScript challenge.
- **Chrome on the runner, with its traffic sent out through the Pi** (`ssh -D` over Tailscale SSH),
  images, fonts and media blocked, downloads capped at 500 KB/s. Fisher's search loaded once. After
  that, Fisher answered "Request Blocked"/"Access Denied", Amazon "Sorry! Something went wrong!" (503) and
  Sigma "Access Denied". I stopped there rather than work round the bot checks, so Amazon, Fisher and Sigma
  prices weren't read.
- Web search found the single-plate seller and the Fisher catalogue number. Every price above was then
  read on the seller's own page.

The Corning family page also lists 5-per-bag black plates (3991, NBS surface, $220.82 per 25), but
3991 isn't in the Opentrons list and costs nearly twice as much per plate as 3915.

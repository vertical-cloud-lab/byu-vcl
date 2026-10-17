# Off-the-shelf holders like V3

On [PR #257](https://github.com/vertical-cloud-lab/byu-vcl/pull/257), @sgbaird asked, out of
curiosity, what Amazon sells that is like this holder. Amazon was searched on 2026-10-08 from
the CubXL Pi, whose residential IP Amazon serves normally. Prices and ratings are as listed
that day, and every figure below is the seller's.

V3, for comparison, is a 50 × 70 × 45 mm black PLA box (29.7 g of filament). A 6.5 mm slot
takes the 6.00 mm blue cooling tube and a 5.5 mm slot the 5.05 mm black power cable. Three
40 × 10 × 3 mm magnets glued to its back hold it to the cabinet. The lines drop in and lift out,
and nothing flexes.

## The nearest things

Nothing listed is quite V3: one part that holds both lines apart, each in a slot sized to it,
and lets them lift out. The nearest things come in five kinds.

| Kind | Example | Price | What the listing says | Against V3 |
|---|---|---|---|---|
| Magnetic zip-tie mount | [Yookeer, 22 mm, 15 pack](https://www.amazon.com/dp/B09M8L4GQV) | $27.99 ($1.87 each) | Rubber-faced magnet with a slot for a tie, about 11.5 lb vertical pull. Also 31 and 43 mm. Ties not included. 4.8★ (390) | The cheapest way to do the job, one per line. The tie has to be cut to take a line out |
| Magnetic P-clamp | [SKNOOY, ½ in, 8 pack](https://www.amazon.com/dp/B0CMQ4TZSH) | $22.99 ($2.87 each) | Rubber-lined 304 stainless clamp, screwed to a magnet. Also ⅝, ¾ and 1 in. 4.1★ (60) | One ½ in clamp would take both lines together, loosely: side by side they are 11.05 mm across. It has to be unscrewed to take a line out |
| Magnetic cord clip | [Lumaneric, 10 pack](https://www.amazon.com/dp/B0DNS99ZWQ) | $13.99 ($1.40 each) | 17 × 7 × 7.5 mm. Fits over a cord up to 6 mm and holds it to steel, 1.5 lb pull. 4.1★ (171) | Made for desk cables. The blue tube is at its 6 mm limit, and a stiff line could peel it off |
| Aquarium dosing-tube holder | [IceCap 4-tube](https://www.amazon.com/dp/B07RRDXKSS) | $33.48 | 73 × 51 × 44 mm. Mounts magnetically through a wall up to ½ in thick. 4.7★ (21) | The closest in form, and nearly V3's size: a magnetic block with slots for small lines. Built to clamp through tank glass, and the tube size isn't listed |
| | [TL Reefs](https://www.amazon.com/dp/B09T1F2YBB) | $28.90 | ¼ in bulkheads for ¼ in OD tubing. Magnets sealed in acrylic, with an O-ring for grip. 4.4★ (27) | The tube is cut and plugged into fittings, so a continuous cable can't go through |
| Magnetic hose and cord hook | [Halder 3688.003](https://www.amazon.com/dp/B0793JSN91) | $36.49 | 100 × 70 × 75 mm, six rubber-encased neodymium magnets. Shaped so cords and air hoses don't slide off. 4.6★ (6) | V3's industrial big brother: a plastic body with magnets in the back and a lip. Sized for shop hoses |
| | [MAG-Mate MX2750HC1](https://www.amazon.com/dp/B07BWTT2MT) | $42.00 | Ceramic cup magnet, 45 lb, with a stainless hook. 4.2★ (74) | The same idea, for hoses and extension cords |

The eight searches returned 232 different listings. Sorted roughly by title, they are 67
magnetic hooks and hangers, 42 zip-tie mounts and magnetic ties, 37 desk cable clips, 36
welding magnets and torch holders, 17 tube holders (aquarium and hydration), 12 magnetic
straps, 4 magnetic clamps and 17 others. Many of the desk clips stick on with adhesive, and
only their clip is magnetic.

## Worth borrowing

- **Rubber on the magnet's face.** On a vertical panel a magnet holds by friction. The zip-tie
  mounts, the Halder holder and the coated hooks all put rubber there. It grips paint better
  than bare metal and doesn't scratch it; Yookeer says its rubber is there to "enhance the
  lateral load carrying capacity".
- **Magnets that screw on.** Ronnie expects the hot glue to fail before the magnets let go.
  Rubber-coated pot magnets with a threaded insert could be bolted to the back instead, e.g.
  [QZYIPI, 43 mm, 8 pack, $15.99](https://www.amazon.com/dp/B0FQJS1QY7) (M4 or ¼-20,
  "up to 30 lb"). The magnet pockets Ronnie plans to print would do the same job.

## Where V3 is ahead

- **Both lines in one part, apart, each in a slot sized to it.** Off the shelf, that takes a
  mount per line, or one clamp that both lines sit loose in.
- **The lines drop in and lift out.** Zip ties have to be cut and clamps unscrewed.
- **Cost.** About 30 g of PLA, well under a dollar, plus the magnets. The cheap kinds above
  cost $1.40–2.87 a mount; the tube holders and shop hooks cost $29–42 each.

## Not checked

- **Every figure is the seller's.** Nothing was bought or tested. Pull ratings are normally
  measured straight off thick steel, and sliding on a painted panel takes a fraction of that
  (see [`../../rebuild/magnet/README.md`](../../rebuild/magnet/README.md#testing-the-magnet)).
- **Amazon's US store only, on one day.** Industrial suppliers such as McMaster-Carr weren't
  searched.
- **The aquarium holders' tube sizes,** apart from TL Reefs' ¼ in.

## How it was searched

- **From the CubXL Pi, with curl,** a desktop browser's User-Agent and one cookie jar, so the
  requests came from a residential IP. 8 searches and 10 product pages, 12–20 s apart and
  capped at 200 kB/s. Every page came back normally, with no CAPTCHA. The same requests
  weren't tried from a runner.
- **Searches:** `magnetic cable holder`, `magnetic cable clips for metal surfaces`,
  `magnetic zip tie mount`, `magnetic hose holder`, `magnetic welding cable holder`,
  `magnetic cable hook heavy duty`, `magnetic tubing holder` and `rubber coated magnetic hook`.
- [`amazon_search_2026-10-08.json`](amazon_search_2026-10-08.json) has all 289 result cards
  (232 different listings; 65 cards were sponsored): query, rank, price, rating, number of
  ratings, "bought in past month" and the sponsored flag.
  [`amazon_products_2026-10-08.json`](amazon_products_2026-10-08.json) has the 10 product
  pages' bullets, descriptions, variants and spec tables. DMiotech's "magnetic" 31 mm saddle
  mount is among them but was left out above: its own description says to screw it down.
- [`parse_amazon.py`](parse_amazon.py) made both files from the saved pages. The pages
  themselves weren't kept.

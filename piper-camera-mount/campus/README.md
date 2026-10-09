# Buying the mount's parts on campus: the ELC and the PSC (9 October 2026)

The Prototyping Lab's drawer has only Phillips pan heads (M2 × 6, 12, 18 and 25; M3 × 6, 10, 18, 25
and 40; M4 to M6) and M2 to M5 nuts, and no M2.5 at all
([photo on #234](https://github.com/vertical-cloud-lab/byu-vcl/pull/234#issuecomment-5960197882)).
Two other campus shops sell or give away things that drawer doesn't have. This page checks both
against what [`BOM.md`](../BOM.md) still needs.

- **ELC:** the ECEn department's Experiential Learning Center, in the Clyde Building.
- **PSC:** the ME department's Project Support Center, in the Engineering Building.

The prices are from the shops' own catalogues on 9 October 2026, read through the CubXL Pi.

## The two shops

| | ELC | PSC |
|---|---|---|
| Where | Front desk 416 Clyde Building, parts room 416B. A vending machine in CB 423 sells parts after hours | Engineering Building, room 107 |
| Hours | Mon–Fri, 8 am to 5 pm | Mon–Fri, 8 am to 5 pm. Closed for the Tuesday devotional |
| Phone | 801-422-4279 | 801-422-7446 |
| How to pay | Cougar Cash, a department card or a research group account | Cougar Cash only. Consumables are free |
| Catalogue | [elcparts.byu.edu](https://elcparts.byu.edu/): 958 items, each with a price, a count and a shelf | [Our Inventory](https://psc.byu.edu/available%20for%20purchase): 80 items, at prices it calls approximate |
| Free | | "tape, glue, wire, nuts, bolts, screws, velcro, and zip ties ... (in reasonable quantities)" |
| Lends | ECEn equipment, such as bench supplies, multimeters and a Joulescope. Loans to other departments go only to faculty, and are free for one semester | [Hand tools, power supplies, drills, soldering irons, heat guns, slow-motion cameras, and weights, scales and force gauges](https://psc.byu.edu/lab%20kits) |

Both are on [the ELC's information page](https://eceshop.byu.edu/information-and-resources) and
[the PSC's home page](https://psc.byu.edu/).

**Neither catalogue lists screw sizes.** The ELC sells screws in two length bands, at one price
per band ("Screws and bolts <=1in in length", $0.06 each). Its nuts are "all sizes" at $0.08. The
PSC lists none of its free hardware. So whether a size is actually in the bins needs a look, or a
photo like the Prototyping Lab one.

**Some ELC counts are negative.** Zip ties stand at −476, for example. A negative count means the
shop doesn't keep that tally up, not that the item is out. Ask at the desk.

## Against what the mount needs

**Fasteners: try the Prototyping Lab drawer first.** [`BOM.md`](../BOM.md) (8 October) lists socket
heads to order. A length check of every joint, made alongside this page on 9 October, reports
that the drawer's M3 × 10, M3 × 18 and M2 × 12 pan heads fit instead, with the nylon M2.5 kit on
the Pi. The fastener rows below are for socket heads, or for anything the drawer is out of.

| Need | Qty | ELC | PSC | Prototyping Lab | What to do |
|---|---|---|---|---|---|
| Raspberry Pi 5, 8 GB | 1 | **$188.00, 2 in stock** | | | PiShop is $175.00 plus shipping (8 October). Buy it at the ELC to have it today on a research group account, or add it to the PiShop order for the HQ Camera to save $13 |
| Pi 5 Active Cooler | 1 | $10.00, 8 in stock | | | Only if the 10 on the #164 order never arrived |
| microSD card | 1 | PNY 64 GB U3, $15.00, 25 in stock | | | Only if the #164 cards never arrived |
| HQ Camera and 6 mm lens | 1 | No. Its only camera is a Camera Module pictured as the v2.1, $16.50 | No | No | PiShop |
| Camera cable, Standard to Mini, 300 mm | 2 | No. Only the 150 mm Pi Zero cable ($6.00), which is too short for the 206 and 212 mm routes | No | No | PiShop, or the 500 mm cables on hand |
| M3 × 12 socket head | 2 + 2 spare | $0.06 if the size is there (cabinet 10) | Free if the size is there | No: M3 × 10 and × 18 pan heads | Look at the ELC and the PSC first |
| M3 × 16 socket head | 8 + 2 spare | As above | As above | No 16 | As above |
| M3 nut | 8 + 4 spare | $0.08 | Free | $0.05 | Any of the three |
| M2.5 × 12, steel, and nut | 4 + 2 spare | $0.06 and $0.08 if the size is there | Probably not: on 1 October sgbaird [wrote](https://github.com/vertical-cloud-lab/byu-vcl/pull/84#issuecomment-5924615427) that neither it nor the Prototyping Lab could supply M2.5 | No M2.5 | The ELC is the only campus chance for steel M2.5. An ISO 4762 M2.5 head is 2.5 mm tall, and the pod's counterbores are 2.0 mm deep, so it would stand 0.5 mm proud. The 9 October check puts M2 × 12 pan heads here instead |
| M2 × 10 socket head | 4 + 2 spare | $0.06 if the size is there | Free if the size is there | No: M2 × 6 and × 12 pan heads | The M2 nuts are on hand |
| USB-C extension, about 2 m, rated 5 A | 1 | **$3.14, 21 in stock**: braided, male to female. The catalogue gives no length or rating | Only USB-C adapters, $1 | | Read its label at the desk. If it's 2 m and rated 100 or 240 W, it's a cheaper test than the AINOPE ($8.99) |
| Zip ties | some | $0.02 each, any length | **Free** | | Free at the PSC. The Amazon pack ($6.99) isn't needed |
| Hook-and-loop ties | some | $0.06 each | **Free** | | Free at the PSC |
| A gauge for the breakaway's pull-off force | | | **Lends** force gauges | | Borrow one instead of buying a luggage scale |
| Hex keys 1.5, 2 and 2.5 mm | | | Lends hand tools | | The lab's own set should do |

For the extension, "rated 5 A" is what [`power/voltage_drop.py`](../power/voltage_drop.py)
assumes: 20 AWG, about 4.78 V at the Pi while it streams. An ordinary 22 AWG one gives about
4.66 V, just above the Pi's 4.63 V warning.

**The ELC also sells a 27 W USB-C supply,** a RasTech XS-GaN-27W at $8.99. Its label gives 5.1 V at
5 A, and 9, 12 and 15 V. Its count isn't kept, so ask. Because it offers 12 V, it would also feed
the PD step-down board in the BOM's optional list.

**To measure what the Pi really draws on the arm:** the 1.5 A and 2.5 A in `voltage_drop.py` are
estimates. The ELC has a Joulescope JS220 (3 A continuous) in CB 413. It also sells USB-C breakout
boards (24-pin, $2.20 male and $3.80 female), which would put the meter in the VBUS line.

**On the 24 V route** (optional in the BOM):
- **The lead:** the ELC sells 16–18 AWG hookup wire at $0.13 a foot. A two-wire lead 4 m long is
  about $3.40. That would replace the two 1.5 m barrel extensions ($5.90).
- **Barrel connectors:** plugs and sockets are $0.80 at the ELC. At the PSC a socket is $0.50, a
  plug $2.70, and screw terminals $0.35.
- **No 5 V, 5 A converter at either shop.** The ELC's buck boards (LM2596, MP1584, Mini-360) are
  rated 3 A or less. At the Pi's 2.5 A busy load they'd be at their limit, and the BOM's
  converter gives 5 A. The PlusRoc converter stays on the list.

## What this changes

Some items can come from campus before anything is ordered:

1. **Zip ties and hook-and-loop ties:** free at the PSC.
2. **Fasteners:**
   - The Prototyping Lab drawer first, as above.
   - For anything it lacks, look in the ELC's cabinet 10 and the PSC's free bins.
   - At the ELC's prices, the 26 screws and 18 nuts on the BOM's Bolt Depot order would come to
     about $3.00 (26 × $0.06 + 18 × $0.08), against $5.12 plus shipping.
   - Order only what none of the three has.
3. **The USB-C extension:** check the ELC's $3.14 one first.
4. **The force gauge:** borrow it from the PSC.
5. **The Pi 5, 8 GB:** at the ELC, if waiting for PiShop is the bigger cost.

The HQ Camera, the 6 mm lens and the 300 mm cables still have to come from PiShop.

## Files

- [`campus_inventory.py`](campus_inventory.py) fetches the ELC catalogue and prints the table
  above. It also turns a saved PSC page into JSON.
  - **The ELC:** its JSON (`/api/items/`) needs no login, and answers a CI runner as well as a campus
    address.
  - **The PSC:** its site answers 403 to the runner, so its page was fetched through the CubXL Pi.
- [`elc_items_2026-10-09.json`](elc_items_2026-10-09.json): the whole ELC catalogue at 16:18 UTC,
  958 items.
- [`psc_items_2026-10-09.json`](psc_items_2026-10-09.json): the PSC's inventory page at 16:16 UTC,
  80 items, with its terms and its free-consumables line.

## Not checked

- **Which screw sizes are in either shop's bins.** Neither catalogue lists them, so a photo of the
  ELC's cabinet 10 and the PSC's bins would settle it.
- **The ELC extension's length and rating.**
- **Stock on the day.** The counts are the shops' own, and some aren't kept.

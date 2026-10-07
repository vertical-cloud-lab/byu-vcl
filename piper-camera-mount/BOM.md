# Bill of materials, what the lab has, and what's still to buy (7 October 2026)

This is one mount: the PiPER's gripper, a Pi 5, the HQ Camera and the Camera Module 3 Wide, powered by
24 V up the arm (option 1 in [`power/README.md`](power/README.md)).

The "Lab has" column comes from a read of every issue, PR and comment in this repo and in
[powder-doser](https://github.com/vertical-cloud-lab/powder-doser), up to 7 October 2026. The terms:

- **On hand:** a person said it arrived, or used it.
- **Ordered:** there's an order, but no one has said it arrived.

Prices were checked on 7 October 2026 unless a date is given.

## Bill of materials

### Printed

| Qty | Part | PAHT-CF, H2D, 0.6 mm | PAHT-CF, H2D, 0.4 mm | PLA, A1 mini |
|---|---|---|---|---|
| 1 | `bracket` | 37.7 g | 31.1 g | 37.8 g |
| 1 | `pod` | 13.5 g | 11.9 g | 14.5 g |
| 1 | `carrier` | 31.7 g | 28.3 g | 34.4 g |
| 4 + 2 | `spacers`, `tag_wedge` | 0.5 g | 0.5 g | 0.6 g |
| | One plate (3 walls, 25 % infill) | 83.5 g, 3 h 47 min | 72.0 g, 3 h 48 min | 87.4 g, 2 h 50 min |

The figures are from [`slice/slice_configs.json`](slice/slice_configs.json). PAHT-CF is recommended
for the parts that stay on the arm (see [Material](README.md#material-paht-cf-on-the-h2d)).

### Electronics

| Qty | Part | Lab has | Evidence |
|---|---|---|---|
| 1 | Raspberry Pi 5 | **On hand:** about 6 or 7 unassigned 1 GB boards. 10 were bought, and 8 were in the office on 4 September. One may since have replaced the CubXL's board, whose USB-C socket was damaged. | [#164](https://github.com/vertical-cloud-lab/byu-vcl/issues/164#issuecomment-5097723625), [#198](https://github.com/vertical-cloud-lab/byu-vcl/issues/198#issuecomment-5546194460), [#234](https://github.com/vertical-cloud-lab/byu-vcl/pull/234#issuecomment-5841723129) |
| 1 | Pi 5 Active Cooler | **Ordered:** 10, on the same PiShop order as the Pi 5s | [#164](https://github.com/vertical-cloud-lab/byu-vcl/issues/164#issuecomment-5097723625) |
| 1 | microSD card | **Ordered:** two 5-packs of SanDisk 32 GB, on the same order | [#164](https://github.com/vertical-cloud-lab/byu-vcl/issues/164#issuecomment-5097723625) |
| 1 | Raspberry Pi HQ Camera (CS) | **None free.** The lab's only HQ Camera is on the OT-2 (meorders 12704). | [#84](https://github.com/vertical-cloud-lab/byu-vcl/pull/84#issuecomment-4407498492) |
| 1 | 6 mm wide-angle CS lens for the HQ | **None.** The OT-2's HQ has a Waveshare 8–50 mm zoom. | [#84](https://github.com/vertical-cloud-lab/byu-vcl/pull/84#issuecomment-4407498492), [#239](https://github.com/vertical-cloud-lab/byu-vcl/issues/239#issuecomment-6046148468) |
| 1 | Camera Module 3 Wide | **On hand:** 10 bought, 2 on the CubXL | [#164](https://github.com/vertical-cloud-lab/byu-vcl/issues/164#issuecomment-5097723625), [#171](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5642454946) |
| 2 | Pi 5 camera cable (Standard–Mini), 300 mm | **None at 300 mm.** 5 × 500 mm were ordered, and there's one 200 mm on the OT-2. The routes are 206 and 212 mm, so 200 mm is too short. | [#164](https://github.com/vertical-cloud-lab/byu-vcl/issues/164#issuecomment-5097723625) |

### Fasteners

| Qty | Part | Where | Lab has |
|---|---|---|---|
| 2 | M3 x 12 socket head (ISO 4762) | Pad into the gripper tab's brass inserts | **None.** The Prototyping Lab drawer sells M3 x 6, 10, 18, 25 and 40 Phillips pan heads, but no 12 or 16 ([#234](https://github.com/vertical-cloud-lab/byu-vcl/pull/234#issuecomment-5960203853)) |
| 8 | M3 x 16 socket head | 4 for the collar clamp, 4 for the pod on its seat | **None** (as above) |
| 8 | M3 hex nut | 4 in the clamp ears, 4 in the seat's slots | **None.** The drawer sells them singly. The doser's M3 locknuts are in use, and too tall for the seat's slots |
| 4 | M2.5 x 12 socket head + 4 M2.5 nuts | HQ Camera, heads in counterbores on the pod's front | **Nylon pan heads only**, in two COMRUN kits ([#234](https://github.com/vertical-cloud-lab/byu-vcl/pull/234#issuecomment-5965195211)). Use steel here: nylon creeps, and this joint sets where the HQ points |
| 4 | M2.5 x 12 + 4 M2.5 nuts | Pi 5, through the spacers into the carrier's nut traps | **On hand:** the COMRUN kits (M2.5 x 12 nylon pan heads, 20 per kit, and 50 nuts) |
| 4 | M2 x 10 socket head + 4 M2 nuts | Camera Module 3 Wide | **Nuts only.** The COMRUN M2 nylon kit has M2 x 6, 8 and 12, not 10 |

### Power (24 V up the arm, 5 V made on the carrier)

| Qty | Part | Lab has |
|---|---|---|
| 1 | 24 V supply, 36 W or more, at the arm's base | **None.** The only Pi supplies are 5.1 V (the official 27 W) |
| 1 | 24 V to 5 V / 5 A USB-C buck converter, on the carrier | **None** |
| about 3–4 m | Lead from the supply to the wrist, with service loops at each joint | **None** |
| 1 | Magnetic breakaway (Adafruit 5521, right-angle USB-C) | **None.** It was proposed on 27 September and not ordered |
| — | Strain relief on the carrier, and ties for the service loops | **Zip ties:** some are in use on the doser. **Hook-and-loop, adhesive mounts, spiral wrap:** none on record |

### Tools and consumables

| For | Lab has |
|---|---|
| Hex keys 2.5 mm (M3), 2 mm (M2.5) and 1.5 mm (M2) | **On hand:** a metric hex-key set ([#126](https://github.com/vertical-cloud-lab/byu-vcl/issues/126#issuecomment-4694533297); its sizes aren't listed). The PSC also lends hex keys |
| Calipers, to check the bore on a test coupon before the real print | **On hand:** Husky 6 in digital calipers ([#119](https://github.com/vertical-cloud-lab/byu-vcl/issues/119#issuecomment-4699888459)) |
| [`exports/fiducials/tags.pdf`](exports/fiducials/tags.pdf) printed at 100 %, glued to the wedges and the target | **On hand:** the ME office colour copier |
| PAHT-CF | **Ordered:** meorders 13433, which replaced 13431, approved 5 October ([#245](https://github.com/vertical-cloud-lab/byu-vcl/pull/245#issuecomment-6000580187)). Either spool size is enough |
| A hardened hotend on the H2D | **On hand:** 0.4 mm hardened steel (left), read from the printer on 27 September. Bambu recommends 0.6 mm for PAHT-CF. A 0.6 mm nozzle was in use in August ([powder-doser#23](https://github.com/vertical-cloud-lab/powder-doser/pull/23#issuecomment-5273911355)), but nothing says whether it's hardened |

## Shopping list

### Needed

| Item | Qty | Where | Each | Total |
|---|---|---|---|---|
| Raspberry Pi HQ Camera CS | 1 | [PiShop.us](https://www.pishop.us/product/raspberry-pi-hq-camera-cs/), in stock | $55.00 | $55.00 |
| 6 mm Wide Angle Lens for HQ Camera CS | 1 | [PiShop.us](https://www.pishop.us/product/6mm-wide-angle-lens-for-raspberry-pi-hq-camera-cs/), in stock | $34.00 | $34.00 |
| Camera Cable for Raspberry Pi 5, **300 mm** (choose the length at checkout) | 2 | [PiShop.us](https://www.pishop.us/product/camera-cable-for-raspberry-pi-5/) | $3.95 | $7.90 |
| M3 x 16 socket head, class 12.9, black oxide | 10 | [Bolt Depot 13638](https://boltdepot.com/Product-Details?product=13638) | $0.12 | $1.20 |
| M3 x 12 socket head, class 12.9, zinc | 4 | [Bolt Depot 23068](https://boltdepot.com/Product-Details?product=23068) | $0.17 | $0.68 |
| M3 hex nut, 18-8 stainless | 12 | [Bolt Depot 4773](https://www.boltdepot.com/Product-Details.aspx?product=4773) | $0.07 | $0.84 |
| M2.5 x 12 socket head, 316 stainless | 6 | [Bolt Depot 22460](https://boltdepot.com/Product-Details?product=22460) | $0.20 | $1.20 |
| M2.5 hex nut, zinc | 6 | [Bolt Depot 18058](https://boltdepot.com/Product-Details?product=18058) | $0.08 | $0.48 |
| M2 x 10 socket head, 18-8 stainless | 6 | [Bolt Depot 6365](https://www.boltdepot.com/Product-Details.aspx?product=6365) | $0.12 | $0.72 |
| Mean Well GST36U24-P1J: 24 V, 1.5 A, US wall plug, 5.5 x 2.1 mm plug | 1 | [TRC Electronics](https://www.trcelectronics.com/products/mean-well-gst36u24-p1j), 325 in stock | $19.48 | $19.48 |
| PlusRoc 12/24 V to 5 V 5 A USB-C converter, potted, 2-pack | 1 | [Amazon B0FD735LFG](https://www.amazon.com/dp/B0FD735LFG), price from 27 September | $15.99 | $15.99 |
| 2.1 mm barrel extension, 1.5 m, 24 AWG | 2 | [Adafruit 327](https://www.adafruit.com/product/327), in stock | $2.95 | $5.90 |
| 2.1 mm jack to screw terminal, for the converter's input | 1 | [Adafruit 368](https://www.adafruit.com/product/368), in stock | $2.00 | $2.00 |
| Magnetic right-angle USB-C adapter, 120 W | 1 | [Adafruit 5521](https://www.adafruit.com/product/5521), in stock | $14.95 | $14.95 |
| Hook-and-loop ties and adhesive tie mounts, for the service loops and the clamp on the carrier | — | any | about $10 | about $10 |
| | | | **Total** | **about $170, plus shipping** |

Notes on the list:

- **Bolt Depot prices** are from its listings. Its site refused a direct check, so confirm them at
  checkout. McMaster, where the lab has an account, sells the same sizes in packs of 50 or 100.
  - The quantities include spares, because nuts get lost in slots.
  - The M3 nuts can come from the Prototyping Lab drawer instead.
- **The 24 V supply** replaces the Mean Well GST36B24-P1J on the 27 September list. That desktop
  version needs a separate IEC C8 mains lead; this one plugs straight into the power strip.
- **The extensions:** two, plus the supply's own cord, reach the wrist. At 24 V they drop about
  0.3 V, at the 0.6 A the converter draws when the Pi takes 2.5 A.
- **The converter:** the PlusRoc doesn't do USB-PD, so set `PSU_MAX_CURRENT=5000` on the Pi
  ([`power/README.md`](power/README.md)). Weigh it before it goes on the carrier.

### Optional

| Item | When | Where | Price |
|---|---|---|---|
| Raspberry Pi 5, 4 GB | If a spare 1 GB board stalls with both cameras. On the CubXL's 1 GB Pi, one of its two 12 MP cameras timed out on 5 of 6 captures, most likely for want of memory ([#171](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5688528247)). An 8 GB board was suggested on [#233](https://github.com/vertical-cloud-lab/byu-vcl/issues/233#issuecomment-5828038858) | [PiShop.us](https://www.pishop.us/product/raspberry-pi-5-4gb/), 1 per order | $110.00 (2 GB $77.50, 8 GB $175.00) |
| H2D hotend, 0.6 mm hardened steel | If it isn't on meorders 13433, and the 0.4 mm clogs on PAHT-CF | [Bambu Lab](https://us.store.bambulab.com/products/bambu-hotend-h2-p2s?id=775924445524066388), 3 October | $17.99 |
| A luggage scale | To measure the breakaway's pull-off force, which no maker publishes | any | about $10 |

Already ordered: PAHT-CF (meorders 13433).

Not for the mount, but still open on the arm: a US mains cord for the PiPER's own supply, which
came with a Chinese one ([#259](https://github.com/vertical-cloud-lab/byu-vcl/issues/259#issuecomment-6001974060)).

## Check before ordering or printing

- **Which gripper the lab has.** No one has answered this on #239.
  - The CAD is for the 0 to 100 mm gripper, whose finger plate is about 164 mm wide.
  - On the older 0 to 70 mm gripper (about 145 mm), the pad has to move 2 mm.
- **What's on meorders 13433:** the 0.5 kg or 1 kg spool, and whether the 0.6 mm hotend was added.
- **Whether the rest of the #164 order arrived.** Only some of it is confirmed:
  - Confirmed: the Pi 5s, the COMRUN kits and the Camera Module 3 Wides.
  - Not confirmed: the Active Coolers, the SD cards and the 500 mm cables.
- **Other projects want the same parts.** On 7 October the atomizer's front viewport was asked to
  get an HQ + Wide pair like this one ([#198](https://github.com/vertical-cloud-lab/byu-vcl/issues/198#issuecomment-6032136284)).
  If that goes ahead, it needs its own HQ Camera, and another spare Pi 5.

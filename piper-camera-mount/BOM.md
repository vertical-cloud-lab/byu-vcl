# Bill of materials, what the lab has, and what's still to buy (7 October 2026, updated 8 October)

This is one mount: the PiPER's gripper, a Pi 5, the HQ Camera and the Camera Module 3 Wide, powered by
the official 27 W supply through a USB-C extension, with 24 V up the arm as the fallback
([`power/README.md`](power/README.md)).

The "Lab has" column comes from a read of every issue, PR and comment in this repo and in
[powder-doser](https://github.com/vertical-cloud-lab/powder-doser), up to 7 October 2026. The terms:

- **On hand:** a person said it arrived, or used it.
- **Ordered:** there's an order, but no one has said it arrived.

Prices were checked on 7 October 2026 unless a date is given. How much RAM the Pi should have is in
[`compute/README.md`](compute/README.md).

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
| 1 | Raspberry Pi 5, **8 GB recommended** | **On hand:** about 6 or 7 unassigned 1 GB boards. 10 were bought, and 8 were in the office on 4 September. One may since have replaced the CubXL's board, whose USB-C socket was damaged. A 1 GB board runs the cameras and OpenCV, but not Claude Code (4 GB minimum) or PyTorch models beside them ([`compute/README.md`](compute/README.md)) | [#164](https://github.com/vertical-cloud-lab/byu-vcl/issues/164#issuecomment-5097723625), [#198](https://github.com/vertical-cloud-lab/byu-vcl/issues/198#issuecomment-5546194460), [#234](https://github.com/vertical-cloud-lab/byu-vcl/pull/234#issuecomment-5841723129) |
| 1 | Pi 5 Active Cooler | **Ordered:** 10, on the same PiShop order as the Pi 5s | [#164](https://github.com/vertical-cloud-lab/byu-vcl/issues/164#issuecomment-5097723625) |
| 1 | microSD card | **Ordered:** two 5-packs of SanDisk 32 GB, on the same order | [#164](https://github.com/vertical-cloud-lab/byu-vcl/issues/164#issuecomment-5097723625) |
| 1 | Raspberry Pi HQ Camera (CS) | **None free.** The lab's only HQ Camera is on the OT-2 (meorders 12704). | [#84](https://github.com/vertical-cloud-lab/byu-vcl/pull/84#issuecomment-4407498492) |
| 1 | 6 mm wide-angle CS lens for the HQ | **None.** The OT-2's HQ has a Waveshare 8–50 mm zoom. | [#84](https://github.com/vertical-cloud-lab/byu-vcl/pull/84#issuecomment-4407498492), [#239](https://github.com/vertical-cloud-lab/byu-vcl/issues/239#issuecomment-6046148468) |
| 1 | Camera Module 3 Wide | **On hand:** 10 bought, 2 on the CubXL | [#164](https://github.com/vertical-cloud-lab/byu-vcl/issues/164#issuecomment-5097723625), [#171](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5642454946) |
| 2 | Pi 5 camera cable (Standard–Mini), 300 or 500 mm | **On hand:** 5 × 500 mm, in sgbaird's office (8 October). There's one 200 mm on the OT-2. The routes are 206 and 212 mm, so 200 mm is too short. 500 mm works, with the extra folded flat on the carrier; 300 mm is tidier, so two are on the PiShop order below. | [#164](https://github.com/vertical-cloud-lab/byu-vcl/issues/164#issuecomment-5097723625), [#245](https://github.com/vertical-cloud-lab/byu-vcl/pull/245) |

### Fasteners

| Qty | Part | Where | Lab has |
|---|---|---|---|
| 2 | M3 x 12 socket head (ISO 4762) | Pad into the gripper tab's brass inserts | **None.** The Prototyping Lab drawer sells M3 x 6, 10, 18, 25 and 40 Phillips pan heads, but no 12 or 16 ([#234](https://github.com/vertical-cloud-lab/byu-vcl/pull/234#issuecomment-5960203853)) |
| 8 | M3 x 16 socket head | 4 for the collar clamp, 4 for the pod on its seat | **None** (as above) |
| 8 | M3 hex nut | 4 in the clamp ears, 4 in the seat's slots | **None.** The drawer sells them singly. The doser's M3 locknuts are in use, and too tall for the seat's slots |
| 4 | M2.5 x 12 socket head + 4 M2.5 nuts | HQ Camera, heads in counterbores on the pod's front | **Nylon pan heads only**, in two COMRUN kits ([#234](https://github.com/vertical-cloud-lab/byu-vcl/pull/234#issuecomment-5965195211)). Use steel here: nylon creeps, and this joint sets where the HQ points |
| 4 | M2.5 x 12 + 4 M2.5 nuts | Pi 5, through the spacers into the carrier's nut traps | **On hand:** the COMRUN kits (M2.5 x 12 nylon pan heads, 20 per kit, and 50 nuts) |
| 4 | M2 x 10 socket head + 4 M2 nuts | Camera Module 3 Wide | **Nuts only.** The COMRUN M2 nylon kit has M2 x 6, 8 and 12, not 10 |

### Power

The PiPER being powered doesn't power the Pi: the arm's supply feeds its motors and the gripper, and the
Pi on the wrist needs its own lead. Try a USB-C extension first; if the Pi reports under-voltage,
change to 24 V up the arm with 5 V made on the carrier ([`power/README.md`](power/README.md)).

| Qty | Part | Lab has |
|---|---|---|
| 1 | Raspberry Pi 27 W USB-C supply (5.1 V / 5 A, 1.2 m lead) | **On hand:** the only Pi 5 supply the lab has |
| 1 | USB-C extension, 240 W (5 A), about 2 m | **None** |
| 1 | Magnetic breakaway (Adafruit 5521, right-angle USB-C), optional | **None.** It was proposed on 27 September and not ordered |
| — | Zip ties: strain relief on the carrier, and the service loops | **Some** are in use on the doser, sizes unknown |

If the extension fails, the cheapest fix keeps it: a PD step-down board on the carrier asks the
official supply for 12 V and makes 5 V next to the Pi ($20.99). The fallback after that is 24 V: a
supply at the base (36 W or more), a 24 V to 5 V / 5 A USB-C converter on the carrier, and about
3–4 m of lead. The lab has none of these. The search found no supply, from any maker, that gives
5 V at 3 A or more on a lead long enough to reach the wrist ([`power/shopping_2026-10-08.md`](power/shopping_2026-10-08.md)).

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
| Camera Cable for Raspberry Pi 5, **300 mm** (pick the length on the page) | 2 | [PiShop.us](https://www.pishop.us/product/camera-cable-for-raspberry-pi-5/), on the same order, 8 October | $3.95 | $7.90 |
| M3 x 16 socket head, class 12.9, black oxide | 10 | [Bolt Depot 13638](https://boltdepot.com/Product-Details?product=13638) | $0.12 | $1.20 |
| M3 x 12 socket head, class 12.9, zinc | 4 | [Bolt Depot 23068](https://boltdepot.com/Product-Details?product=23068) | $0.17 | $0.68 |
| M3 hex nut, 18-8 stainless | 12 | [Bolt Depot 4773](https://www.boltdepot.com/Product-Details.aspx?product=4773) | $0.07 | $0.84 |
| M2.5 x 12 socket head, 316 stainless | 6 | [Bolt Depot 22460](https://boltdepot.com/Product-Details?product=22460) | $0.20 | $1.20 |
| M2.5 hex nut, zinc | 6 | [Bolt Depot 18058](https://boltdepot.com/Product-Details?product=18058) | $0.08 | $0.48 |
| M2 x 10 socket head, 18-8 stainless | 6 | [Bolt Depot 6365](https://www.boltdepot.com/Product-Details.aspx?product=6365) | $0.12 | $0.72 |
| USB-C extension, 240 W (5 A), 6.6 ft, male to female | 1 | [Amazon B09FDWG61C](https://www.amazon.com/dp/B09FDWG61C) (AINOPE), in stock | $8.99 | $8.99 |
| Zip ties, 400 pack, 4 + 6 + 8 + 12 in, black nylon | 1 | [Amazon B08TVLYB3Q](https://www.amazon.com/dp/B08TVLYB3Q), in stock | $6.99 | $6.99 |
| | | | **Total** | **about $118, plus shipping** |
| Raspberry Pi 5, **8 GB**, recommended | 1 | [PiShop.us](https://www.pishop.us/product/raspberry-pi-5-8gb/), in stock, 8 October | $175.00 | **about $293 with it** |

Notes on the list:

- **Bolt Depot prices** are from its listings. Its site refused a direct check, so confirm them at
  checkout. McMaster, where the lab has an account, sells the same sizes in packs of 50 or 100.
  - The quantities include spares, because nuts get lost in slots.
  - The M3 nuts can come from the Prototyping Lab drawer instead.
- **Amazon prices** were checked through the CubXL Pi on 8 October 2026, delivering to Provo.
- **The camera cables:** the 500 mm ones from #164 are in sgbaird's office and will do. Since the HQ
  Camera and lens come from PiShop anyway, two 300 mm cables cost $7.90 more and leave nothing
  to fold.
- **The 8 GB Pi 5** is for running Claude Code, PyTorch models or several models at once on the
  wrist. Its price is from PiShop on 8 October, when the 1 GB and 2 GB boards were out of stock and
  the 4 GB was $110. The reasoning and measurements are in [`compute/README.md`](compute/README.md).
- **The extension** goes between the official 27 W supply's 1.2 m lead and the Pi, about 3.2 m in
  all. It should hold the Pi at about 4.78 V while it streams, against an under-voltage limit of
  4.63 V, if its wires are really 20 AWG. No listing says, so check it on the arm with
  `vcgencmd pmic_read_adc EXT5V_V` and `vcgencmd get_throttled`
  ([`power/README.md`](power/README.md#if-youd-rather-try-an-extension-first-8-october-2026)).
- **The zip ties:** the 4 in ones hold the lead to the carrier 20 to 30 mm from the plug, and the 8
  and 12 in ones hold the service loops on the arm.

### Optional

| Item | When | Where | Price |
|---|---|---|---|
| Magnetic right-angle USB-C adapter, 120 W | A breakaway, so a snagged lead pulls apart instead of the socket. It adds another mated pair, about 0.03 V at 1.5 A | [Adafruit 5521](https://www.adafruit.com/product/5521) | $14.95 |
| 24 V route: Mean Well GST36U24-P1J, PlusRoc 24 V to 5 V USB-C converter, two 1.5 m barrel extensions, a jack to screw terminal | Only if the Pi reports under-voltage through the extension, and you'd rather not rely on PD | [TRC Electronics](https://www.trcelectronics.com/products/mean-well-gst36u24-p1j) $19.48, [Amazon B0FD735LFG](https://www.amazon.com/dp/B0FD735LFG) $15.99, [Adafruit 327](https://www.adafruit.com/product/327) 2 × $2.95, [Adafruit 368](https://www.adafruit.com/product/368) $2.00 | $43.37 |
| PD step-down board, 12 V in from USB-C PD, 5 V / 5 A out (eleUniverse) | If the extension leaves the Pi under-voltage: keep the official supply and the extension, and have the board ask for 12 V and make 5 V on the carrier. 34 g, with a fan; the carrier has no place for it yet | [Amazon B0FR8VRWFJ](https://www.amazon.com/dp/B0FR8VRWFJ), in stock, 8 October | $20.99 |
| iUniker 5 V / 4 A supply (5.25 V out, 1.5 m lead) | Another cheap test in place of the official supply: its 0.15 V more puts the Pi at about 4.90 V through the extension. No PD | [Amazon B097P2NLVH](https://www.amazon.com/dp/B097P2NLVH), in stock, 8 October | $9.99 |
| Raspberry Pi 5, 4 GB, instead of the 8 GB | Meets Claude Code's 4 GB minimum, but not with the cameras and a PyTorch model beside it | [PiShop.us](https://www.pishop.us/product/raspberry-pi-5-4gb/), in stock, 8 October | $110.00 |
| Raspberry Pi AI HAT+, 13 TOPS (Hailo-8L) | For YOLO or segmentation at video rate: YOLO11n at 157 fps against about 7 fps on the Pi's CPU. It needs room on the carrier that the CAD doesn't have | [PiShop.us](https://www.pishop.us/product/raspberry-pi-ai-hat-13-tops/), 8 October | $76.95 (26 TOPS $119.95) |
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
  - Confirmed: the Pi 5s, the COMRUN kits, the Camera Module 3 Wides and the 500 mm cables.
  - Not confirmed: the Active Coolers and the SD cards.
- **Other projects want the same parts.** On 7 October the atomizer's front viewport was asked to
  get an HQ + Wide pair like this one ([#198](https://github.com/vertical-cloud-lab/byu-vcl/issues/198#issuecomment-6032136284)).
  If that goes ahead, it needs its own HQ Camera, and another spare Pi 5.

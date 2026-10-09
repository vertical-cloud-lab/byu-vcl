# Bill of materials, what the lab has, and what's still to buy (7 October 2026, updated 8 and 9 October)

This is one mount: the PiPER's gripper, a **Raspberry Pi 5 8 GB**, the HQ Camera and the Camera
Module 3 Wide, powered by the official 27 W supply through a USB-C extension, with 24 V up the arm as
the fallback ([`power/README.md`](power/README.md)).

The "Lab has" column comes from a read of every issue, PR and comment in this repo and in
[powder-doser](https://github.com/vertical-cloud-lab/powder-doser), up to 7 October 2026. The terms:

- **On hand:** a person said it arrived, or used it.
- **Ordered:** there's an order, but no one has said it arrived.

The prices in [The order](#the-order-9-october-2026) were fetched on 9 October 2026 between 16:22 and
16:45 UTC, through the CubXL Pi's campus connection (Amazon showed delivery to Provo). The records are
in [`prices_2026-10-09.json`](prices_2026-10-09.json). Other prices carry their own date. How much RAM
the Pi should have is in [`compute/README.md`](compute/README.md).

## The order (9 October 2026)

### PiShop.us

| Qty | Item | Each | Total | Stock |
|---|---|---|---|---|
| 1 | [Raspberry Pi 5, 8 GB](https://www.pishop.us/product/raspberry-pi-5-8gb/) | $175.00 | $175.00 | In stock |
| 1 | [Raspberry Pi HQ Camera, CS mount](https://www.pishop.us/product/raspberry-pi-hq-camera-cs/) | $55.00 | $55.00 | In stock |
| 1 | [6 mm Wide Angle Lens for the HQ Camera, CS](https://www.pishop.us/product/6mm-wide-angle-lens-for-raspberry-pi-hq-camera-cs/) | $34.00 | $34.00 | In stock, 36 left |
| 2 | [Camera Cable for Raspberry Pi 5](https://www.pishop.us/product/camera-cable-for-raspberry-pi-5/), **choose 300 mm** (the page opens on 500 mm, $3.95) | $2.65 | $5.30 | In stock |
| | | **Subtotal** | **$269.30** | plus shipping |

### Amazon

| Qty | Item | Each | Stock |
|---|---|---|---|
| 1 | [AINOPE USB-C extension, 240 W, 6.6 ft, B09FDWG61C](https://www.amazon.com/dp/B09FDWG61C). The listing's other sizes are USB-A two-packs, so take the 6.6 ft | $8.99 | In stock, shipped by Amazon |
| 1 | [HAVE ME TD zip ties, 400 pack, 4 + 6 + 8 + 12 in, B08TVLYB3Q](https://www.amazon.com/dp/B08TVLYB3Q) | $6.99 | In stock |
| | **Subtotal** (free shipping over $35, or with Prime) | **$15.98** | |

### ME Prototyping Lab drawer (117 EB)

Stainless Phillips pan heads and nuts, priced on the bins in
[@mcwilliams03's photo](https://github.com/vertical-cloud-lab/byu-vcl/pull/234#issuecomment-5960197882)
(2 October). What each one is for is in [Fasteners](#fasteners).

| Take | Part | Each | Total |
|---|---|---|---|
| 3 | M3 × 10 | $0.10 | $0.30 |
| 10 | M3 × 18 | $0.10 | $1.00 |
| 12 | M3 nut | $0.05 | $0.60 |
| 10 | M2 × 12 | $0.10 | $1.00 |
| 12 | M2 nut | $0.05 | $0.60 |
| | **Subtotal** | | **$3.50** |

The counts include spares: one M3 × 10, two of each other screw and four of each nut. The four M2.5
screws and nuts for the Pi 5 come from the lab's nylon kit.

**Total: $288.78, plus PiShop's shipping.**

**On campus first** ([`campus/README.md`](campus/README.md), read the same day):

- **Zip ties:** the PSC (107 EB) gives them away, which saves the $6.99 Amazon pack.
- **USB-C extension:** the ELC sells a $3.14 one, but its catalogue gives no length or rating. Read
  the label at the desk before choosing it over the AINOPE.
- **Pi 5 8 GB:** the ELC had two, at $188.00. That's $13 more than PiShop, but you'd have it the
  same day.

### Only if the lab's aren't there

All three were on the [#164](https://github.com/vertical-cloud-lab/byu-vcl/issues/164#issuecomment-5097723625)
order of 29 July, together with the ten Pi 5s, which did arrive. No one has said these did, so check
the boxes before buying.

| Item | #164 ordered | Each |
|---|---|---|
| [Raspberry Pi Active Cooler](https://www.pishop.us/product/raspberry-pi-active-cooler/). The 8 GB board is meant to run models, so it needs one; the carrier leaves room for it | 10 | $10.95 |
| Raspberry Pi 27 W USB-C supply, US, [white](https://www.pishop.us/product/raspberry-pi-27w-usb-c-power-supply-white-us/) or [black](https://www.pishop.us/product/raspberry-pi-27w-usb-c-power-supply-black-us/). Earlier versions of this file said the lab had only one; #164 ordered ten | 10 | $12.95 |
| [SanDisk Ultra microSDHC 32 GB, blank](https://www.pishop.us/product/microsd-card-32-gb-class-10-blank/) (Raspberry Pi's own 32 GB card is out of stock) | two 5-packs | $14.95 |

## Fasteners

**Nothing needs ordering.** All 22 screws and 20 nuts come from the Prototyping Lab drawer or the
nylon M2.5 kit. [`cad/fastener_fit.py`](cad/fastener_fit.py) checked every length against the CAD and
AgileX's gripper. It tests the drawer's sizes, three pan-head standards and a socket head. Its results
are in [`exports/fastener_fit.json`](exports/fastener_fit.json).

| Joint | Screws | Nuts | Use | How it fits | From |
|---|---|---|---|---|---|
| Pad → the gripper tab's brass inserts | 2 | | **M3 × 10** | 4.0 mm into the tab's 6.5 mm insert. The CAD was drawn for a 12, which the drawer doesn't have. An 18 goes right through the tab | Drawer |
| Collar clamp | 4 | 4 × M3 | **M3 × 18** | 4.7 mm past the nut with the split closed; the 10 doesn't reach the nut | Drawer |
| Pod → seat | 4 | 4 × M3 | **M3 × 18** | 2.8 mm past the nut, and 2.3 mm short of the bottom of the blind hole. A 25 bottoms out | Drawer |
| HQ Camera → pod | 4 | 4 × M2 | **M2 × 12** | M2 through the camera's M2.5 holes, since the drawer has no M2.5. The Ø4 mm head sits 0.3 to 0.4 mm below the pod's face in its Ø5 × 2 mm counterbore, and the tip is 0.4 mm past the nut on the lab's 2.0 mm board | Drawer |
| Camera Module 3 Wide → pod | 4 | 4 × M2 | **M2 × 12** | 2.8 mm past the nut | Drawer |
| Pi 5 → spacers → carrier | 4 | 4 × M2.5 | **Nylon M2.5 × 12**, the kit's longest | 1.7 mm past the nut. An 18 would hit the gripper | Nylon kit |

"Past the nut" is from the tip to the nut's far face, with each nut at its thickest (ISO 4032) and
pulled up against its trap.

**Why not M2.5 on the HQ Camera.** The bracket's seat covers two of the four HQ heads, so all four
must sit inside their counterbores, which are Ø5.0 mm and 2.0 mm deep.

- **Socket heads won't do.** The M2.5 socket head the earlier BOM listed is 2.5 mm tall, so the two
  covered ones would hold the pod 0.5 mm off its seat.
- **The nylon pan heads are marginal.** An M2.5 pan head is Ø5.0 mm, the same as the printed
  counterbore, so it may not drop in. Even if it does, the kit's 12 mm screw only reaches the nut's
  far face on the lab's 2.0 mm board; Raspberry Pi's drawing says 1.4 mm. A board that thick is why
  the same screws fell short on the OT-2 lid mount
  ([#234](https://github.com/vertical-cloud-lab/byu-vcl/pull/234)).
- **A 14 mm M2.5 would work.** It reaches 2.0 mm past the nut, and its tips stay 0.4 mm in front
  of the J6 flange face. A 16 goes 1.5 mm past the face.
- **So M2 from the drawer.** The camera weighs 83 g with its lens. M2 is loose in M2.5 holes, but
  that doesn't matter once the screws are tight, because the bosses set the camera's tilt. Centre
  the lens mount in the plate's hole before tightening.

**Don't use:**

- Washers under the camera screws, since they lift the heads out of the counterbores.
- M3 × 6 or × 10 for the clamp or pod. They don't reach the nut.
- M3 × 25 for the pod, which bottoms out at 20.3 mm.
- M2 × 18 for either camera. Its tip would sit behind the J6 flange face.

**In the Wide's picture:** the Wide already sees the collar's top ear, at the edge of its picture.
The front upper clamp screw's tip pokes 4.1 mm out of that ear, and lands right on the edge of the
Wide's 102° view, at mid-height. The design's 16 would just graze it too. If it bothers you, file
2 mm off that one screw. No other screw shows in either camera.

**Tools:** the PSC (107 EB) lends them.

- A #1 Phillips with a shaft at least 45 mm long and under 6.5 mm thick, for the M3s and the nylon
  M2.5s. The tab screws' heads sit 33 mm down their Ø7 channels (39 mm once the pod is on), so a
  stubby won't reach.
- A #0 Phillips for the M2s. Some M2 pan heads take a #1, as McMaster's do.
- Hex keys aren't needed unless you swap in socket heads.

**Order of work:** the README's [assembly order](README.md#hardware) already suits these screws.
Three things to know:

- **Drive the clamp screws before the Pi 5 goes on.** The board covers their channels, 35 mm above
  the heads.
- **Fit both cameras to the pod before the pod goes on.** The seat covers two of the HQ heads.
- **The pod's screws can be driven with the gripper on the arm.** Their heads face the arm, 1.7 to
  4.3 mm in front of the J6 flange face. They sit 44 to 51 mm off the J6 axis, and the arm behind
  the flange stays within about 33 mm of it.

**If the drawer runs out**, McMaster (where the lab has an account) sells the same 18-8 stainless parts
in packs of 100. Prices were read on 9 October with no login.

| Part | McMaster | Pack of 100 |
|---|---|---|
| M3 × 10 pan head | [92000A120](https://www.mcmaster.com/92000A120/) | $6.78 |
| M3 × 18 pan head (Ø6 × 2.5 mm head, #1) | [92000A127](https://www.mcmaster.com/92000A127/) | $12.29 |
| M2 × 12 pan head (Ø4 × 1.7 mm head, #1) | [92000A019](https://www.mcmaster.com/92000A019/) | $9.66 |
| M3 nut | [91828A211](https://www.mcmaster.com/91828A211/) | $5.68 |
| M2 nut | [91828A111](https://www.mcmaster.com/91828A111/) | $7.41 |

McMaster's own heads were checked too. They fit everywhere the drawer's do.

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
for the parts that stay on the arm (see [Material](README.md#material-paht-cf-on-the-h2d)). The PLA set
went to the A1 mini on 8 October ([record](slice/print_2026-10-08/README.md)).

### Electronics

| Qty | Part | Lab has | Evidence |
|---|---|---|---|
| 1 | Raspberry Pi 5, **8 GB** | **To buy** ([The order](#the-order-9-october-2026)). The lab's spares are about 6 or 7 unassigned 1 GB boards, which run the cameras and OpenCV but not Claude Code (4 GB minimum) or PyTorch models beside them ([`compute/README.md`](compute/README.md)) | [#164](https://github.com/vertical-cloud-lab/byu-vcl/issues/164#issuecomment-5097723625), [#198](https://github.com/vertical-cloud-lab/byu-vcl/issues/198#issuecomment-5546194460), [#234](https://github.com/vertical-cloud-lab/byu-vcl/pull/234#issuecomment-5841723129) |
| 1 | Pi 5 Active Cooler | **Ordered:** 10, on the same PiShop order as the Pi 5s | [#164](https://github.com/vertical-cloud-lab/byu-vcl/issues/164#issuecomment-5097723625) |
| 1 | microSD card | **Ordered:** two 5-packs of SanDisk 32 GB, on the same order | [#164](https://github.com/vertical-cloud-lab/byu-vcl/issues/164#issuecomment-5097723625) |
| 1 | Raspberry Pi HQ Camera (CS) | **To buy.** The lab's only HQ Camera is on the OT-2 (meorders 12704). | [#84](https://github.com/vertical-cloud-lab/byu-vcl/pull/84#issuecomment-4407498492) |
| 1 | 6 mm wide-angle CS lens for the HQ | **To buy.** The OT-2's HQ has a Waveshare 8–50 mm zoom. | [#84](https://github.com/vertical-cloud-lab/byu-vcl/pull/84#issuecomment-4407498492), [#239](https://github.com/vertical-cloud-lab/byu-vcl/issues/239#issuecomment-6046148468) |
| 1 | Camera Module 3 Wide | **On hand:** 10 bought, 2 on the CubXL | [#164](https://github.com/vertical-cloud-lab/byu-vcl/issues/164#issuecomment-5097723625), [#171](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5642454946) |
| 2 | Pi 5 camera cable (Standard–Mini), 300 or 500 mm | **On hand:** 5 × 500 mm, in sgbaird's office (8 October). There's one 200 mm on the OT-2. The routes are 206 and 212 mm, so 200 mm is too short. 500 mm works, with the extra folded flat on the carrier; 300 mm is tidier, so two are on the PiShop order. | [#164](https://github.com/vertical-cloud-lab/byu-vcl/issues/164#issuecomment-5097723625), [#245](https://github.com/vertical-cloud-lab/byu-vcl/pull/245) |

### Power

The PiPER being powered doesn't power the Pi: the arm's supply feeds its motors and the gripper, and the
Pi on the wrist needs its own lead. Try a USB-C extension first; if the Pi reports under-voltage,
change to 24 V up the arm with 5 V made on the carrier ([`power/README.md`](power/README.md)).

| Qty | Part | Lab has |
|---|---|---|
| 1 | Raspberry Pi 27 W USB-C supply (5.1 V / 5 A, 1.2 m lead) | **On hand:** at least one. #164 ordered ten more with the Pi 5s |
| 1 | USB-C extension, 240 W (5 A), about 2 m | **To buy** ([The order](#the-order-9-october-2026)) |
| 1 | Magnetic breakaway (Adafruit 5521, right-angle USB-C), optional | **None.** It was proposed on 27 September and not ordered |
| — | Zip ties: strain relief on the carrier, and the service loops | **Some** are in use on the doser, sizes unknown. A 400-pack is on the order |

The extension goes between the official supply's 1.2 m lead and the Pi, about 3.2 m in all. It should
hold the Pi at about 4.78 V while it streams, against an under-voltage limit of 4.63 V, if its wires
are really 20 AWG. No listing says, so check it on the arm with `vcgencmd pmic_read_adc EXT5V_V` and
`vcgencmd get_throttled`
([`power/README.md`](power/README.md#if-youd-rather-try-an-extension-first-8-october-2026)). Tie the
lead to the carrier 20 to 30 mm from the plug with a 4 in tie; the 8 and 12 in ties hold the service
loops on the arm.

If the extension fails, the cheapest fix keeps it: a PD step-down board on the carrier asks the
official supply for 12 V and makes 5 V next to the Pi ($20.99). The fallback after that is 24 V: a
supply at the base (36 W or more), a 24 V to 5 V / 5 A USB-C converter on the carrier, and about
3–4 m of lead. The lab has none of these. The search found no supply, from any maker, that gives
5 V at 3 A or more on a lead long enough to reach the wrist ([`power/shopping_2026-10-08.md`](power/shopping_2026-10-08.md)).

### Tools and consumables

| For | Lab has |
|---|---|
| Phillips #1 (shaft 45 mm or more) and #0 screwdrivers, for the drawer's pan heads and the nylon kit ([Fasteners](#fasteners)) | **On hand at the PSC** (107 EB), which lends them. The lab's metric hex-key set ([#126](https://github.com/vertical-cloud-lab/byu-vcl/issues/126#issuecomment-4694533297)) is only needed with socket heads |
| Calipers, to check the bore on a test coupon before the real print | **On hand:** Husky 6 in digital calipers ([#119](https://github.com/vertical-cloud-lab/byu-vcl/issues/119#issuecomment-4699888459)) |
| [`exports/fiducials/tags.pdf`](exports/fiducials/tags.pdf) printed at 100 %, glued to the wedges and the target | **On hand:** the ME office colour copier |
| PAHT-CF | **Ordered:** meorders 13433, which replaced 13431, approved 5 October ([#245](https://github.com/vertical-cloud-lab/byu-vcl/pull/245#issuecomment-6000580187)). Either spool size is enough |
| A hardened hotend on the H2D | **On hand:** 0.4 mm hardened steel (left), read from the printer on 27 September. Bambu recommends 0.6 mm for PAHT-CF. A 0.6 mm nozzle was in use in August ([powder-doser#23](https://github.com/vertical-cloud-lab/powder-doser/pull/23#issuecomment-5273911355)), but nothing says whether it's hardened |

## Optional

| Item | When | Where | Price |
|---|---|---|---|
| Magnetic right-angle USB-C adapter, 120 W | A breakaway, so a snagged lead pulls apart instead of the socket. It adds another mated pair, about 0.03 V at 1.5 A | [Adafruit 5521](https://www.adafruit.com/product/5521), in stock, 9 October | $14.95 |
| PD step-down board, 12 V in from USB-C PD, 5 V / 5 A out (eleUniverse) | If the extension leaves the Pi under-voltage: keep the official supply and the extension, and have the board ask for 12 V and make 5 V on the carrier. 34 g, with a fan; the carrier has no place for it yet | [Amazon B0FR8VRWFJ](https://www.amazon.com/dp/B0FR8VRWFJ), 9 October: no stock line, delivery 28 October to 19 November | $20.99 |
| 24 V route: Mean Well GST36U24-P1J, PlusRoc 24 V to 5 V USB-C converter, two 1.5 m barrel extensions, a jack to screw terminal | Only if the Pi reports under-voltage through the extension, and you'd rather not rely on PD | [TRC Electronics](https://www.trcelectronics.com/products/mean-well-gst36u24-p1j) $19.48, [Amazon B0FD735LFG](https://www.amazon.com/dp/B0FD735LFG) $15.99, [Adafruit 327](https://www.adafruit.com/product/327) 2 × $2.95, [Adafruit 368](https://www.adafruit.com/product/368) $2.00 (7–8 October) | $43.37 |
| iUniker 5 V / 4 A supply (5.25 V out, 1.5 m lead) | Another cheap test in place of the official supply: its 0.15 V more puts the Pi at about 4.90 V through the extension. No PD, and its listing now says it isn't made for the Pi 5's full power | [Amazon B097P2NLVH](https://www.amazon.com/dp/B097P2NLVH), in stock, 9 October | $9.99 |
| Raspberry Pi 5, 4 GB, instead of the 8 GB | Meets Claude Code's 4 GB minimum, but not with the cameras and a PyTorch model beside it | [PiShop.us](https://www.pishop.us/product/raspberry-pi-5-4gb/), in stock, 9 October | $110.00 |
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
  - Not confirmed: the Active Coolers, the SD cards and the ten 27 W supplies.
- **That the drawer still has M2 × 12 and M3 × 18.** They were there in the 2 October photo. The PSC
  (107 EB) gives screws away and is the next place to look.
- **The fits on the printed PLA set**, before the PAHT-CF one: an M3 nut in a clamp-ear trap and a
  seat slot, an M2 pan head in an HQ counterbore (it should sit below the face), and the bore on the
  gripper body.
- **Other projects want the same parts.** On 7 October the atomizer's front viewport was asked to
  get an HQ + Wide pair like this one ([#198](https://github.com/vertical-cloud-lab/byu-vcl/issues/198#issuecomment-6032136284)).
  If that goes ahead, it needs its own HQ Camera, and another spare Pi 5.

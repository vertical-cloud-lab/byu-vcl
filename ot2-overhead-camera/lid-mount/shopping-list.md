# Shopping list: OT-2 lid camera mount

**Where:** the [ME Prototyping Lab](https://www.me.byu.edu/me-prototyping-lab), **117 EB** (Nick
Hawkins's shop). It's open Mon–Fri 8–5, closed Tue 10:30–12 for devotional; 801-422-6297,
byuprototypinglab@gmail.com. It sells the fasteners it has in stock, so ask a TA at the counter.
**Pay** with the department card from the front office, and keep the itemized receipt.

**Nothing M2.5 needs buying.** Every M2.5 part comes from the lab's black nylon COMRUN kit
(below), which is fine because those parts carry only the camera and the Pi 5, a few newtons
([sgbaird](https://github.com/vertical-cloud-lab/byu-vcl/pull/234#issuecomment-5924717073)).
The M3 and M4 parts are the stainless pan heads in the lab's drawer. All sizes are metric.

### From the nylon M2.5 kit, already in the lab

COMRUN's 350-piece black nylon M2.5 kit ([Amazon B0CKBWQSNY](https://www.amazon.com/dp/B0CKBWQSNY/)).
The lab has two of them, and one M2 kit that this mount doesn't use. The kit holds Phillips pan
heads in 6, 8 and 12 mm, nuts, washers, and male–female and female–female standoffs; the full
list is in [`hardware/amazon/README.md`](hardware/amazon/README.md).

| ☐ | Take | Part | Goes |
|---|---|---|---|
| ☐ | 4 | **PM M2.5 × 12** pan head, the kit's longest | camera → deck: up through the camera's corner holes |
| ☐ | 4 | **M2.5 nut** | in the traps on top of the deck, for those screws |
| ☐ | 4 | **M2.5 6 + 6 male–female standoff** (6 mm hex body, 6 mm stud) | Pi 5 → deck: each stud goes down through the deck |
| ☐ | 4 | **M2.5 nut** | in the traps in the deck's underside, onto the studs |
| ☐ | 4 | **PM M2.5 × 6** pan head | down through the Pi 5 into the standoffs |

- **The camera screws:** the M2.5 × 12 is just long enough. Its tip ends level with the top of
  the nut, about four threads in, and the camera and lens hang about 0.5 N on each screw.
- **The standoffs** replace the printed 5 mm spacers and lift the Pi 1 mm. They stay on the
  deck when the Pi comes off, so the nuts underneath can't drop out.
- **If an M2.5 × 6 stops before the Pi is snug,** put a kit washer under its head; COMRUN gives
  no thread depth for the standoffs.
- **Fallback with the printed spacers:** M2.5 × 12 down through the Pi and spacers into the
  underside nuts.
- **Tightening:** small nylon Phillips heads strip easily, so tighten until snug and stop.

### What the lab's drawer holds

From [@mcwilliams03's photo](https://github.com/vertical-cloud-lab/byu-vcl/pull/234#issuecomment-5960197882)
of 2026-10-02: stainless Phillips pan-head screws and hex nuts, M2 to M6. The drawer has no
M2.5, so those come from the nylon kit above.

| Size | In the drawer | Each | For this mount |
|---|---|---|---|
| M3 | 6, 10, 18, 25 and 40 mm screws; nuts | $0.10; nuts $0.05 | **10 mm**, the only length that fits as printed. 18 mm only with the 2 mm shims |
| M4 | 6, 12, 18, 25 and 40 mm screws; nuts | $0.15; nuts $0.05 | 18 mm, for phase 2 (12 mm at a pinch) |

An M3 × 10 ends level with the floor of the nut slot, 0.6 mm (about one thread) past a
full-thickness nut. That is enough here: the screws only hold the deck down, and the plastic
around the nut would give way long before the thread. An M3 × 18 without the shims bottoms
out 1 mm before its head seats, so it feels tight but doesn't clamp the deck; don't force
it. The 6 mm screw doesn't reach the nut, and the 25 and 40 mm ones are far too long.

### Phase 1: the mount taped to the lid

The M2.5 parts come from the kit above; these are the only ones to buy.

| ☐ | Need | Buy | Part | Goes | Length | If they're out |
|---|---|---|---|---|---|---|
| ☐ | 4 | 6 | **M3 × 10 mm Phillips pan head**, stainless, from the drawer above. 12, 14 or 16 mm, with any head, also fit | deck → posts | 10–16 mm. **Not 18** without the shims: the hole in each post is blind and stops 17 mm below the head | McMaster [92000A120](https://www.mcmaster.com/92000A120/) (the same screw) |
| ☐ | 4 | 6 | **M3 hex nut**, from the drawer | slid into the slots in the posts. One also does the fit coupon's nut test | | [91828A211](https://www.mcmaster.com/91828A211/) |

### Phase 2: only if the window gets drilled

| ☐ | Need | Buy | Part | Goes | Length | If they're out |
|---|---|---|---|---|---|---|
| ☐ | 4 | 4 | **M4 × 18 mm Phillips pan head**, stainless, from the drawer. Not a socket head: the head hangs under the lid, and the pipette head passes 9.1 mm below it | up through the lid into the base, from inside the robot | 12 mm and up. The 18 reaches 6.5 mm past the nut; a 12 only 0.5 mm | [92000A227](https://www.mcmaster.com/92000A227/) (the same screw) |
| ☐ | 4 | 4 | **M4 hex nut**, from the drawer | in the base's nut traps | | [91828A231](https://www.mcmaster.com/91828A231/) |
| ☐ | 4 | 4 | **M4 nylon washer**, 4.3 × 9 mm. A plain steel one will do if that's all they have; tighten gently | under the M4 heads | | [95610A550](https://www.mcmaster.com/95610A550/) |

### Other lengths and heads

Lengths are measured from under the head. [`cad/fastener_fit.py`](cad/fastener_fit.py) tries
every standard length and four head types against the CAD model, with each nut at its
thickest ([results](exports/fastener_fit.json)).

| Screw | Works | Shortest (tip through its nut) | Longest, and what stops it |
|---|---|---|---|
| M2.5, camera → deck | 12–18 mm; the kit's 12 is flush with the nut | 12.1 mm | 18.4 mm: the underside of the Pi 5 |
| M2.5, Pi 5 → nylon standoffs | 6 mm | 1.6 mm (the board) | about 7.6 mm: the bottom of the 6 mm standoff's thread |
| M2.5, Pi 5 → printed spacers → deck (fallback) | 12 mm and up | 11.3 mm | 38 mm: the space kept clear for turning the lens rings |
| M3, deck → posts | 10–16 mm | 9.4 mm | 17.0 mm: the bottom of the screw hole in the post |
| M3, with the 2 mm deck shims | 12–18 mm | 11.4 mm | 19.0 mm |
| M4, base → lid | 12 mm and up | 11.5 mm, on a 5 mm window with a 0.8 mm washer | nothing in reach |

If only 18 mm or longer M3s are to hand, fit the 2 mm shims, or run a 1/8 in (3.2 mm) drill
2–4 mm further down each post's hole before the nuts go in. With the shims, the posts reach
only 0.5 mm into their sockets, less than the 0.8 mm chamfer on their tops, so the screws
rather than the sockets locate the deck. For a new base, `m3_screw_len` in
[`cad/lid_mount.py`](cad/lid_mount.py) sets the depth of the holes; the base sent to the
printer on 2026-10-02 has the 17 mm ones.

**Heads.** Socket (ISO 4762), button (ISO 7380) and Phillips pan heads all fit the M2.5
and M3 joints, so they can be mixed, and the kit's nylon pan heads fit. That includes the older DIN 7985 pan head, whose M3
head is Ø6.0 mm rather than Ø5.6 mm; it still clears the Pi 5 by 4.0 mm in plan. The
official drawings leave about Ø5.4 mm around each of the camera's corner holes and Ø5.8 mm
around each of the Pi 5's, and those M2.5 heads are Ø4.5–5.0 mm. Skip countersunk (flat)
heads: nothing is countersunk. Only the M4 heads are constrained, because they hang under
the window, above the pipette head. With the washer, a button head hangs 3.0 mm below the
window, a Phillips pan 3.9 mm and a socket head 4.8 mm, against 9.1 mm of clearance in
Opentrons' CAD, less about 1.5 mm of estimated window sag.

**Tools.** For the parts above, a Phillips screwdriver: #1 for the nylon M2.5 and the M3
pan heads, #2 for the M4s. Press firmly while turning: small Phillips heads cam out, and nylon
ones strip. A stubby or offset driver helps with the camera screws, which go up past the
camera's lens mount. Hex keys only if you swap in hex-drive heads: 1.5 mm for M2.5 button
heads, 2 mm for M2.5 socket and M3 button heads, 2.5 mm for M3 socket and M4 button heads.

### Free at the Project Support Center, 107 EB

The [PSC](https://psc.byu.edu/) gives out tape, velcro, nuts and screws free in reasonable
quantities, and lends tools. It's also the next place to try for any size the Prototyping Lab
doesn't have.

- ☐ **Painter's or gaffer tape**, to tape the base down in phase 1
- ☐ **A #1 Phillips screwdriver to borrow**, for the kit's nylon M2.5 pan heads and the drawer's M3 pan heads (#2 for its M4s). Hex keys only if you use hex-drive heads instead; see [Tools](#other-lengths-and-heads)
- ☐ Optional: a scrap of 1–2 mm black adhesive foam, as a light seal under the base

### Already on hand

- The camera, lens, C–CS adapter, Pi 5, Active Cooler and camera cable came on ME order 12704 ([#84](https://github.com/vertical-cloud-lab/byu-vcl/pull/84)).
- The printed parts (base, deck, spacers and shims) print on the lab's A1 mini. The deck,
  spacers and shims (plate 2) were printed on 2026-10-01, and the base (plate 1), in black, on 2026-10-02.
- Two 350-piece COMRUN kits of black nylon M2.5 hardware, which supply every M2.5 part
  ([above](#from-the-nylon-m25-kit-already-in-the-lab); [sgbaird on #84](https://github.com/vertical-cloud-lab/byu-vcl/pull/84#issuecomment-5924615427)),
  and one M2 kit, not needed here.

Full details are in the [README](README.md#hardware) and [`hardware/README.md`](hardware/README.md).

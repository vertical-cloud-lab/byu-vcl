# Shopping list: OT-2 lid camera mount

**Where:** the [ME Prototyping Lab](https://www.me.byu.edu/me-prototyping-lab), **117 EB** (Nick
Hawkins's shop). It's open Mon–Fri 8–5, closed Tue 10:30–12 for devotional; 801-422-6297,
byuprototypinglab@gmail.com. It sells the fasteners it has in stock, so ask a TA at the counter.
**Pay** with the department card from the front office, and keep the itemized receipt.

Stainless or zinc-plated steel both work. All sizes are metric.

### Phase 1: the mount taped to the lid

| ☐ | Need | Buy | Part | Goes | Length | If they're out |
|---|---|---|---|---|---|---|
| ☐ | 8 | 10 | **M2.5 × 14 or 16 mm screw**, socket head (button or Phillips pan heads also fit) | camera → deck (4), Pi 5 → deck (4) | 14–16 mm; 12 at a pinch. From 18 mm up, the camera screws hit the Pi 5 above them | McMaster [91292A018](https://www.mcmaster.com/91292A018/) (16 mm) |
| ☐ | 8 | 10 | **M2.5 hex nut** | in the deck's nut traps | | [91828A113](https://www.mcmaster.com/91828A113/) |
| ☐ | 4 | 6 | **M3 × 12, 14 or 16 mm screw**, button head (socket or Phillips pan heads also fit) | deck → posts | 10–16 mm. **Not 18:** the hole in each post is blind and stops 17 mm below the head | [92095A184](https://www.mcmaster.com/92095A184/) (16 mm) |
| ☐ | 4 | 6 | **M3 hex nut** | slid into the slots in the posts. One also does the fit coupon's nut test | | [91828A211](https://www.mcmaster.com/91828A211/) |

### Phase 2: only if the window gets drilled

| ☐ | Need | Buy | Part | Goes | Length | If they're out |
|---|---|---|---|---|---|---|
| ☐ | 4 | 4 | **M4 × 16 mm button head screw (ISO 7380)**, or a Phillips pan head. Not a socket head: the head hangs under the lid, and the pipette head passes 9.1 mm below it | up through the lid into the base, from inside the robot | 12 mm and up; 14–16 best | [92095A194](https://www.mcmaster.com/92095A194/) |
| ☐ | 4 | 4 | **M4 hex nut** | in the base's nut traps | | [91828A231](https://www.mcmaster.com/91828A231/) |
| ☐ | 4 | 4 | **M4 nylon washer**, 4.3 × 9 mm. A plain steel one will do if that's all they have; tighten gently | under the M4 heads | | [95610A550](https://www.mcmaster.com/95610A550/) |

### Other lengths and heads

Lengths are measured from under the head. [`cad/fastener_fit.py`](cad/fastener_fit.py) tries
every standard length and three head types against the CAD model, with each nut at its
thickest ([results](exports/fastener_fit.json)).

| Screw | Works | Shortest (tip through its nut) | Longest, and what stops it |
|---|---|---|---|
| M2.5, camera → deck | 14–16 mm; 12 at a pinch | 12.1 mm | 17.4 mm: the underside of the Pi 5 |
| M2.5, Pi 5 → deck | 12 mm and up | 11.3 mm | 38 mm: the space kept clear for turning the lens rings |
| M3, deck → posts | 10–16 mm | 9.4 mm | 17.0 mm: the bottom of the screw hole in the post |
| M3, with the 2 mm deck shims | 12–18 mm | 11.4 mm | 19.0 mm |
| M4, base → lid | 12 mm and up | 11.5 mm, on a 5 mm window with a 0.8 mm washer | nothing in reach |

If the M3s only come in 18 mm or longer, fit the 2 mm shims, deepen the holes before the
base is printed (`m3_screw_len` in [`cad/lid_mount.py`](cad/lid_mount.py) sets their depth),
or run a 1/8 in (3.2 mm) drill 2–4 mm further down each post's hole before the nuts go in.

**Heads.** Socket (ISO 4762), button (ISO 7380) and Phillips pan (ISO 7045) heads all fit
the M2.5 and M3 joints, so they can be mixed. The official drawings leave about Ø5.4 mm
around each of the camera's corner holes and Ø5.8 mm around each of the Pi 5's, and those
M2.5 heads are Ø4.5–5.0 mm. Skip countersunk (flat) heads: nothing is countersunk. Only the
M4 heads are constrained, because they hang under the window, above the pipette head. With
the washer, a button head hangs 3.0 mm below the window, a Phillips pan 3.9 mm and a socket
head 4.8 mm, against 9.1 mm of clearance in Opentrons' CAD, less about 1.5 mm of estimated
window sag.

**Tools.** Hex keys: 1.5 mm for M2.5 button heads, 2 mm for M2.5 socket and M3 button
heads, 2.5 mm for M3 socket and M4 button heads. Phillips: #1 for M2.5 and M3, #2 for M4.
Hex drives are the easier choice for the camera screws, which are driven up past the
camera's lens mount, and small stainless Phillips heads cam out easily.

### Free at the Project Support Center, 107 EB

The [PSC](https://psc.byu.edu/) gives out tape, velcro, nuts and screws free in reasonable
quantities, and lends tools. It's also the next place to try for any size the Prototyping Lab
doesn't have.

- ☐ **Painter's or gaffer tape**, to tape the base down in phase 1
- ☐ **Hex keys to borrow:** 2 mm (M2.5 socket heads, M3 button heads) and 2.5 mm (M4 button heads, or M3 socket heads). Other heads take other tools; see [Tools](#other-lengths-and-heads)
- ☐ Optional: a scrap of 1–2 mm black adhesive foam, as a light seal under the base

### Already on hand

- The camera, lens, C–CS adapter, Pi 5, Active Cooler and camera cable came on ME order 12704 ([#84](https://github.com/vertical-cloud-lab/byu-vcl/pull/84)).
- The printed parts (base, deck, spacers and shims) print on the lab's A1 mini.

Full details are in the [README](README.md#hardware) and [`hardware/README.md`](hardware/README.md).

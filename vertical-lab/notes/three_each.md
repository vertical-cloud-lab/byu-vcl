# Three each of the OT-2, CubXL, H2D, A2L and A1 mini: what it takes (#303, PR #318 round 10, lab stream)

Sterling asked on #303 (2026-11-03) for three each. Only the unmerged side branch `claude/issue-303-20261103-1726`
(`39db74a`) ever built them; this lab has **one** OT-2, one CubXL, one H2D, one A1 mini and **no A2L**. This note works
out what adding the rest takes from today's plan (`notes/tray_plan.md`, `out/tray_plan.json`, `setup_lab.py`). It is
arithmetic on the drawn footprints, not a render: nothing here has been placed in a scene or passed through
`setup_lab.py fit`. Numbers marked *est* are ours; *model* is the footprint our CadQuery model uses; *spec* is a maker's
figure (check them before ordering anything).

## To add

| Machine | Have | Add | W x D x H, mm | Mass, kg | Draw, W | Source |
|---|---|---|---|---|---|---|
| Opentrons OT-2 | 1 | 2 | 624 x 568 x 662 | about 20 (est from memory of Opentrons' sheet, unverified) | 180 | footprint: `out/tray_plan.json` tray A (the model); power: `services.POWER` (docs.opentrons.com, idle 90-120, active 100-180) |
| CubXL + EZstat corrosion set-up | 1 | 2 | 1328 x 605 x 538 as drawn (frame alone 740 x 605 x 488) | about 30 (est: frame, steppers, cell, potentiostat) | 100 (est) + the EZstat | frame: Genmitsu PROVerXL 4030 V2, `lab_models/equipment.py` (SainSmart spec); the rest of the width is the cell and potentiostat |
| Bambu Lab H2D | 1 | 2 | 492 x 514 x 626 | about 31 (spec, from memory, unverified) | 1050 avg, 1320 max under 3 min | `lab_models/equipment.py`; `services.POWER` (Bambu, snippet) |
| Bambu Lab A1 mini | 1 | 2 | 360 x 296 x 482 as drawn (with spool holder; Bambu's bare printer is smaller) | about 5.5 (spec, unverified) | 150 max | `lab_models/equipment.py`; `services.POWER` (Bambu TDS, snippet) |
| Bambu Lab A2L | 0 | 3 | 544 x 529 x 505 | 12.8 | **400 (est, not published; the A1's class)** | `a2l.py` on the side branch: Bambu's published envelope and build volume as quoted by 3D Printing Industry, 2026-06-02 |

Five more things need a decision that the arithmetic can't make: the A2L's draw, the H2D's and A1 mini's masses, and
whether each has Ethernet (see Services).

## The room on a tray

A tray is 2450 x 864 mm (`vlm.TRAY_W/D`), 50 mm rim, so 2350 x 764 inside. Every tray carries a UPS standing on its side
at the back right (x 609-1060, y 276-362) and the dock plate's bracket (x from 1143, y 180-420), so the usable row is
**x -1175 to 1100 (about 2275 mm) by y -382 to 276 (about 658 mm)**. Nothing is two deep: the deepest machine here is 605
mm, so one row per tray. Two camera posts per tray stand between machines, about 120 mm each. That leaves about 2000 mm
of machine width less 50 mm gaps:

| Row | Width, mm | Fits |
|---|---|---|
| CubXL set-up + OT-2 (as tray A) | 1328 + 624 + 50 = 2002 | yes, it is tray A today |
| H2D + A1 mini (as tray C) | 492 + 360 + 50 = 902 | yes, with 1100 mm free |
| H2D + A1 mini + A2L | 492 + 360 + 544 + 100 = 1496 | yes |
| 3 x A2L | 3 x 544 + 100 = 1732 | yes |
| 3 x OT-2 | 3 x 624 + 100 = 1972 | tight, yes |
| CubXL + CubXL | 2 x 1328 | **no**; frames alone (740) would pass, but not with their cells |

Pairing each CubXL with an OT-2 (as today) is the natural unit: the corrosion work moves vials between them.

## Option 1: UPS-safe (5 new trays)

| New tray | Contents | Tallest, mm | Slot span, mm | Mass, kg | Draw, W (loss and Pis in) |
|---|---|---|---|---|---|
| A2, A3 | CubXL + OT-2 | 703 (camera head) | 750 each | about 80 | 297 (tray A's figure) |
| C2, C3 | H2D + A1 mini | 692 | 725 each | about 65 | 1244 (tray C's figure) |
| P | 3 x A2L | 515 (short camera posts, as trays H and J) | 550 | about 65 | about 1250 (3 x 400 + Pis + 3 % loss, est) |

Tray masses: the UPS is 23 kg, the cameras and Pis a few kg; all are far inside a *light* tray's 230 kg
(`kardex_tall.py`: light 230, medium 360, strong 500 kg). The load per area is not a constraint.

**Why not three printers on one tray?** The UPS is a 1500 VA Eaton 5PX1500, about 1350 W. Tray C already draws 1244 W
(H2D 1050 + A1 mini 150), so any tray holding an H2D can't also hold a 400 W A2L at full draw. This option keeps
every tray at or under what the lab already checks. Per-tray column room: **5 trays = 2 x 750 + 2 x 725 + 550 = 3500
mm**.

## Option 2: dense (4 new trays)

A2, A3 as above, and C2, C3 each carry H2D + A1 mini + A2L (1496 mm wide, slot 725). Column room 2 x 750 + 2 x 725 =
2950 mm. Each printer tray draws about 1050 + 150 + 400 + 44 = 1650 W flat out, **over the UPS's 1350 W**. Ways out: a
2200 VA UPS (its depth is unchecked; the strip the 5PX1500 stands in is 86 mm thick and 447 deep, so a longer unit may
not fit), or a cap in the scheduler so the H2D and A2L never heat together (the H2D's 1320 W peak lasts under 3 min), or
a 240 V feed to the tray (the 230 V model of the same UPS is still 1350 W, so that alone doesn't help). Cheaper in column
room (550 mm), dearer in electronics and scheduling.

## Trays, slots and the third Shuttle

Free room today: Shuttle 1's rear column 390 mm (3300-3690) and front column 290 mm, Shuttle 2's rear 15 mm and front 290
mm, and nothing under 475 mm is a tray (the UPS is 437 mm). So **none of the new trays fits**: one has to bring a **third
Shuttle**, the same unit as the first two (`vlm.COLUMNS` pattern):

| Shuttle 3 column | Range, mm | Option 1 | Option 2 |
|---|---|---|---|
| rear | 300-3690 (3390) | A2, A3, C2, C3 = 2950, 440 left | A2, A3, C2, C3 = 2950, 440 left |
| front, upper | 1950-3690 (1740) | P at 1950, 1190 left | free |
| front, lower | 300-793 (493) | free | free |

Option 1 uses 3500 of about 5620 mm; Option 2 uses 2950 and leaves room for two more trays later. Tray labels A2... are
only labels; the plan's letters run A-O today.

**Floor:** `vlm.SHUTTLE_X` puts Shuttle 3 at x = 3630 beyond Shuttle 2, that is x = 7260, which stands on the **Aconity
MIDI (x 6950)**; the packaging station (x 10050) stays clear. Shuttle 1's west side is the sieve cell and rePowder. The
Aconity has to move east (it is 2450 wide, so to about x 10200 or later) or across the aisle onto the south row, and
the packaging station with it, or the north row is extended beyond 10050. The hall's east wall isn't modelled, so how far
the row may extend is a question about the real building. Shuttle 3 also needs a dock, a target post and a pivot gap
the way `setup_lab.FLOOR_PLAN` does it (800 mm of floor between units); `fit` would need to re-check all of that.

## Services

- **Power.** Each presented position uses one dock on a 30 A breaker at 208/120 V (5 kVA continuous at 80 %,
  `notes/services.md`), so a tray's 1250-1650 W is well inside the dock; the limit is the tray's UPS, above. The Shuttle
  itself is its own 208 V three-phase supply (#53), for Shuttle 3 as for the others. The all-on adds (Option 1) are 2 x
  297 + 2 x 1244 + 1250 = **4330 W**; Option 2 is 594 + 2 x 1650 = 3890 W. The existing all-on figure is 7015 W for two
  Shuttles; Shuttle 3's own enclosure would carry only its own.
- **Heat in Shuttle 3.** Option 1 all on: 4330 W / (5.5 W/m2K x 55.9 m2) = **14 K unventilated** (est method of
  `notes/services.md`), 2600 m3/h for a 5 K rise or 1300 m3/h for 10 K. That is more air than the two existing
  Shuttles' "printing in storage" case (680-1360 m3/h): printers running in a closed steel shaft need a filtered fan and a roof
  outlet at Shuttle 3 from the start. Idle (60 W a tray, est): 5 trays = 300 W, 1 K.
- **Whether a stored tray is powered at all** is still an open question to Kardex (`ask_kardex` in
  `out/services.json`). If not, nothing prints while stored, and only the tray at the opening runs: then the heat and the
  UPS issues vanish but so does the point of loading printers.
- **Exhaust for the printers.** The H2D is enclosed, with its own filtered exhaust (carbon and particle), the A1 mini
  and A2L are open frames: PLA/PETG only unless a hood sits over the tray. In a closed shaft an open printer's
  ultrafine particles stay in the column, so either the Shuttle's roof fan carries them out to a filter, or each printer
  tray carries a Sentry Air-class ductless hood (tray M has one, 1030 x 717 mm; it doesn't fit beside these rows).
  Recommend: roof fan for Shuttle 3 plus PLA/PETG-only on open frames.
- **Network.** One 10 Gbit RJ45 per dock module. Per tray: one small switch (5 ports) behind the plate for the printers
  and Pis. The A1 mini is Wi-Fi only as far as we know, which won't work inside a steel cabinet: confirm or use a USB
  Ethernet route (an unverified assumption). Bambu's LAN mode through a cabinet needs the same check for the H2D and A2L.
- **Chilled water, N2, air:** none of these machines uses any, so the tray's other four couplings sit unused on A2, A3,
  C2, C3 and P.

## The arm

The UR10e on its MiR250 stands at x = 0 in front of the opening and reaches 1300 mm (`out/reach.json`): **83 % of the
presented tray's 50 mm grid at 100 mm over the floor, 77 % at 250 mm, deepest 800 mm**. The missing 17-23 % is the
far corners, the outer 200-300 mm of a 2450 mm row. On a full row that matters: a machine centred beyond about
|x| = 900 mm isn't reachable at its front, so on A2/A3 the **vial seat has to sit near the centre**
(today's CubXL seat in tray A is, per `reach.py`: header gap 571 mm), and a printer's plate-removal needs the same
treatment, or the tray stops short of the opening, or the Shuttle's arm has a rail. Only the seat the arm touches matters,
not the whole machine. **This is unchecked for the new items:** run `reach.py` with the three-printer rows' seats.
It also means that three OT-2s on one tray (1972 mm wide) are poor: only the middle one sits in the arm's reach.

Handling time per tray swap is the extractor's, about 6 s from R2 to the opening (`out/services.json`), unchanged; a
third Shuttle gives a third opening and so needs either a third arm and MiR250 or the one MiR driving between three docks.

## Assumed

- One row of machines per tray, camera posts of today's sizes, the UPS where it is.
- The A2L draws 400 W, is 12.8 kg, and is laid out like an A1 (no CAD or measured data). H2D and A1 mini masses and the OT-2's from memory, unchecked.
- A third Shuttle the same as the others is purchasable, its floor space exists, and the Aconity and packaging station move.
- Nothing about cost, lead time, or the tray fit as measured by `fit` (not run).

## Recommendation

Option 1 for now: 5 trays, a third Shuttle (one more opening, a dock, a roof fan, an Aconity move), no UPS change. Costs
two more UPSs than Option 2 and 550 mm of column; buys none of the UPS or scheduling risk. A decision for Sterling: the
Aconity's move, whether stored trays are powered, and whether the A1 mini's Wi-Fi works in a steel shaft.

# Measuring the rePowder for the viewport cameras

The camera mounts in [`atomizer-viewport-cameras/`](../../README.md) were designed from training-video frames. Every
machine dimension in them is a guess, good to 15–25 %. That is not close enough for a part that has to push onto
the machine. These sheets show what to measure, one area of the machine at a time. Each measurement has a letter
on a photo, with where the tape goes, the tool, and the number the model uses now. There is a blank beside it for
yours.

You don't need Onshape or any of the variable names. Write the numbers down, and whoever updates the model can
match them up using [`field_sheet.csv`](field_sheet.csv).

## Bring

- Metric tape measure, and a 300 mm steel rule
- Calipers. The grey cover is about 162 mm across, wider than 150 mm calipers open. Use 200 mm calipers if you
  have them; if not, see F1 on sheet 1.
- A phone with a level app. On an iPhone it is in **Measure → Level**, and most Android phones have one. Lay the
  phone flat on a surface and it reads that surface's angle.
- A fridge magnet (M4)
- Nitrile gloves. Wear them whenever you touch the machine: the grey cover on the front port soaks up skin oil (#126).
- The sheets, printed ([`rePowder-measuring-guide.pdf`](rePowder-measuring-guide.pdf), one sheet a page), or open on
  your phone

## Before you start

- **The machine must be cold and not running.** The lid window gets hot. Check with whoever has the machine booked.
- **The grey cover on the front port pulls straight off by hand.** It is AMAZEMET's LED light, with its cable on
  the little pod. Let it hang from that cable and don't unplug it. Put it back the same way round, with the pod at
  the bottom (6 o'clock).
- **Leave the shiny nut under the cover alone.** It holds the port glass in, and turning it can break the seal.
- **Don't press on any glass.** For F9 and T6, bring the end of the rule just up to the glass, so that it touches.

## Order of work

If time is short, do the ones marked **FIRST**. There are 17 of them, and the fit-test prints can't be made
without them. **NEXT** places and aims the units, and **IF TIME** checks clearances the model already allows
for.

| Sheet | Area | FIRST |
|---|---|---|
| [1](1_front_cover_on.jpg) | Front port, grey cover on | F1, F2, F3, F6 |
| [2](2_front_cover_closeup.jpg) | Looking into the grey cover | F8, F9 |
| [3](3_front_cover_off.jpg) | Front port, cover off | F11, F14 |
| [4](4_front_side_sketch.jpg) | Side-view sketch of the front port: where the depths and the tilt go | (no new ones) |
| [5](5_left_sight_glass.jpg) | Left side: the small round window on the door | L1, L2, L3 |
| [6](6_lid_window.jpg) | Furnace lid window, face on | T1, T2 |
| [7](7_lid_from_front.jpg) | Furnace lid, from the front | T7, T8 |
| [8](8_whole_machine.jpg) | Whole machine: scale, heights, the lid's swing | M1, M2 |

Do sheets 1 and 2 with the cover on, then take it off for sheet 3.

## A few tricks

- **Finding a centre.** For a height to the centre of a window, measure to its top edge and to its bottom edge, and
  write down both. The same goes for distances across to a centre.
- **Across flats, without big calipers (F1, F8).** Hold two books, or a book and a block, flat against opposite
  flats of the 12-sided cover. Then measure between them. Flat to flat is about 3 % less than corner to corner. If
  you could only do corner to corner, write the number and say so.
- **Round things (T9, M1).** Wrap the tape round and write the circumference. We divide by 3.14.
- **Depths (F9, F13, F16, T6).** Stand the rule's end on the far surface, square to it, and read where it passes
  the near surface. Sheet 4 shows the front port's depths side on.
- **Angles (F14, T7).** Lay the phone flat on the face and write what the level app says. Do F14 twice, on the
  nut's face and on the flat chamber face beside it: if the chamber face isn't vertical either, we need both.
- **Photograph each measurement** with the tape or calipers in place. A photo lets us catch a misread or a mix-up
  later, and it settles questions the numbers can't, such as L3 (what kind of fitting the door window has).
- **If one doesn't make sense on the machine,** write what you see instead, and take a photo. Being wrong about
  the shape is worth knowing too.

## Reporting back

Any of these works:

- Reply on [#198](https://github.com/vertical-cloud-lab/byu-vcl/issues/198) with `F1 161`, `F2 88 x 44 x 52`, and so
  on, plus the photos.
- Photograph the filled-in sheets and post them there.
- Fill in the `measured` column of [`field_sheet.csv`](field_sheet.csv).

The numbers then go into the **Machine dimensions (measure these)** tab of the
[Onshape document](https://cad.onshape.com/documents/f6b439dfa2a88fd1d41e85b7/w/30ec7826dedfab13d9c6d67b). The
CSV's `onshape_variable` column says which entry each one replaces, and every part rebuilds from them.

## How the sheets are made

[`sheets.py`](sheets.py) holds the text of every measurement: the letter, priority, description, the model's
current value and the Onshape variable. [`make_guide.py`](make_guide.py) draws them onto the frames in
[`../frames/`](../frames/) and writes the sheets, the PDF and `field_sheet.csv`. To change a description or a
mark, edit those files and run `python make_guide.py` in this folder (needs Pillow).

The photos are stills from the lab's training videos. Where a sheet says a part is on the left or the right, it
means as seen standing at the front of the machine, facing the aus500 label.

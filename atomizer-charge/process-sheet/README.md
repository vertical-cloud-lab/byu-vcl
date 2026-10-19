# Process sheets for the Al cup and plug

Process sheets for making the 6063 charge cups and their vented plugs, for
[PR #277](https://github.com/vertical-cloud-lab/byu-vcl/pull/277) and [#248](https://github.com/vertical-cloud-lab/byu-vcl/issues/248).
Print [`process_sheet.pdf`](process_sheet.pdf) (Letter, landscape, three pages) and take it to the shop.
[`process_sheet.md`](process_sheet.md) has the same tables, for reading on a phone.

| Page | What it covers |
| --- | --- |
| 1, [cup](process_sheet-p1.png) | A cup from one 3" blank: face both ends to 2.750", center drill, 1/2" drill 2.25" deep, measure the bore |
| 2, [plug](process_sheet-p2.png) | A plug on the end of a blank, turned to its own cup's bore + .0005", 15° lead-in, #60 vent, parted off at .5625" |
| 3, [record](process_sheet-p3.png) | One row per cup-and-plug set. It carries each cup's measured bore to its plug, then the masses to the bag |

The sizes are the ones the first parts were made to (#222: Gage's cups, Ronnie's plugs), restated in
[this comment](https://github.com/vertical-cloud-lab/byu-vcl/pull/277#issuecomment-6155056001), not the older
[#232](https://github.com/vertical-cloud-lab/byu-vcl/pull/232) drawing. The cleaning and contamination rules come from #232's
machining-contamination note of 2026-10-07.

## Choices that weren't spelled out before

- **The 2.25" depth is to full diameter**, as in #232's CAD and the usual drawing convention, so the drill goes 2.40"
  past the point where its tip touches the face. Nobody recorded whether the first cups' 2.25" was measured to the
  tip or to full diameter. If it was to the tip, new cups have about 0.8 g more room for powder. Cups are filled by
  weight, so this doesn't change a run, but it's a reason to keep each run's cups from one batch.
- **The plug target is the bottom of the fit window, + .0005".** The window is + .0005" to + .0008". The
  [Oct 7 composition-spread note](https://github.com/vertical-cloud-lab/byu-vcl/pull/232#issuecomment-6032144024) found that
  + .0008" brings the 9/16" plug's cup close to yield.
- **The cup needs no parting tool.** Each cup is one 3" blank faced on both ends, as Gage made them, so it can be made
  in the Prototyping Lab as well as the CTB shop. The plug is parted off, which is why it goes to the CTB shop, where
  parting is allowed. Without a parting tool, the plug can be sawn off about 1/32" long and faced to length. To do
  that it has to be held by its finished OD, so use soft jaws.
- **The plug's top edge is deburred by hand after parting.** The presentation clip chamfers it on the lathe before
  parting. Either works, since the edge plays no part in the fit, and the hand method needs no extra setup.
- **The vent is drilled .65" deep before parting.** That way the parting cut breaks into it, and no pip is left. A
  #60 jobber drill has 11/16" of flute, so .65" is within reach.
- **No needle file for the optional channel.** The no-files rule from the contamination note wins, so use a 1/16" end
  mill or a single hacksaw kerf.
- **Speeds and feeds are starting points** for HSS tools on a manual lathe, worked from rpm = 3.82 × sfm / diameter
  and kept low enough to hand-feed. The shop's staff and posted rules come first.

Still open: the sliding clearance for the compaction (hydraulic-press) plugs. The record sheet's variants box says to ask
Sterling before turning one.

## Rebuilding

```bash
pip install pymupdf
python process_sheet.py    # -> process_sheet.pdf, process_sheet-p{1,2,3}.png, process_sheet.md
```

All the text is in the tables at the top of `process_sheet.py`. Edit it there and rebuild, so that the PDF, the PNGs and
the Markdown stay the same. The PDF is printed with headless Chrome, which comes with GitHub's runners; set `CHROME`
to use a different browser.

# Shop drawing: charge cup and plug, as made

![Shop drawing of the charge cup and plug](cup_plug.png)

[PDF](cup_plug.pdf) (one US-Letter sheet; printed at 100 % the cup is 1:1 and the plug 3:1) · built by
[`cup_plug.py`](cup_plug.py)

This drawing is for the cups and plugs as they were made for the first runs, so that new ones match them. The drawing on
PR [#232](https://github.com/vertical-cloud-lab/byu-vcl/pull/232) (`cad/drawings/charge_parts.pdf`) is the earlier
design: a 2.500" cup 1.875" deep and a .375" plug. Neither drawing should replace the other until #232 merges.

## Where each number comes from

| | Value | Source |
| --- | --- | --- |
| Bar | 3/4" 6063, McMaster [1640T16](https://www.mcmaster.com/1640T16/), OD as received | #222 |
| Blank | 3.000" | the sawn blanks, #277 |
| Cup length | 2.750", both ends faced | Gage, [#222](https://github.com/vertical-cloud-lab/byu-vcl/issues/222) |
| Cup bore | 1/2" drill, 2.25" deep, pointed (118°) bottom | Gage, #222 |
| Plug length | .5625" (9/16") | Ronnie, #222 |
| Plug diameter | its own cup's measured bore + .0005" (+.0008" max); the first ones were .508" for their cups | #222; "aim for .0005" from #232's Oct 7 composition-spread notes |
| Vent | #60 (.040") through, on center | #222 |
| Nose lead-in, top chamfer, bore-mouth and outside chamfers | .060" × 15°, .015" × 45°, .015" × 45°, .020" × 45° | #232's design (`charge_cad.py`) |
| Optional channel (press runs) | about .05" wide × .03" deep across the top, through the vent | #248, as modelled in `../presentation/clips.py` |
| Thin-wall version | 5/8" drill, same depth, .250" plug, +.0005" only | #232, `composition_spread.py`; #264 |
| Cleaning and contamination notes | cut dry or with light oil, no abrasives, IPA flush | #232 README (Edison, Oct 7) |

## Assumed, or still open

- **The 2.25" depth is drawn to the drill point.** Gage's note says "2.25 in (cone-shaped end)" without saying
  whether it was measured to the point or to the full diameter. To the point is where it lands if the tailstock is
  zeroed when the point touches the face, which is the usual way to do it on a manual lathe. If it was to the full
  diameter, the bore is .15" deeper and holds about 0.8 g more powder. Change `DEPTH` in `cup_plug.py` if so.
- **The press-run (sliding) plug has no clearance yet**, so the drawing gives only the bore finish and the channel
  for that version, and says to ask before making one.
- **Masses** in the table are for nominal stock. The bar's OD tolerance (±.014") moves them by about 4 %.

## Rebuilding

```bash
pip install matplotlib
python cup_plug.py      # writes cup_plug.pdf and cup_plug.png
```

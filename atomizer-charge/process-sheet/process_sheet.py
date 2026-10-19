"""Process sheets for the Al charge cup and its plug, as made (#222, #248, #277).

    pip install pymupdf
    python process_sheet.py    # -> process_sheet.pdf, process_sheet-p{1,2,3}.png, process_sheet.md

One source for three outputs: the PDF (Letter, landscape, to print and take to the shop), a PNG of each page, and
process_sheet.md, the same tables for reading on a phone. Edit the tables here and rebuild, so the three can't drift.
Page 1 is the cup, page 2 the plug, page 3 the record sheet that carries each cup's bore over to its plug.

The sizes are the as-made ones from #222 (Gage's cups, Ronnie's plugs), as restated in #277, not the older #232
drawing: cup 2.750" long with a 1/2" drill 2.25" deep, plug .5625" long with a #60 vent and its diameter matched to
its own cup's bore. The cleaning rules are from #232's machining-contamination note (2026-10-07). Speeds are
starting points for HSS tools in 6063 on a manual lathe, worked from rpm = 3.82 x sfm / diameter, and kept inside
what a manual lathe and a hand-fed tailstock can do.

The PDF is printed by headless Chrome, which ships on GitHub runners; set CHROME to use another binary.
"""
import html
import math
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
PDF, MD = HERE / "process_sheet.pdf", HERE / "process_sheet.md"
REV, DATE = "A", "2026-10-19"
PR = "https://github.com/vertical-cloud-lab/byu-vcl/pull/277"

INK, INK2, RULE, ACCENT, SECTION = "#0b0b0b", "#52514e", "#c9c7c1", "#2a78d6", "#e9e7e2"

HEADER = {
    "Material": '6063-T52 aluminum, Ø3/4" round bar, McMaster 1640T16',
    "Stock": '3.000" blanks sawn 10/14, in the metal box on the table by the atomizer',
    "Machines": "Manual lathe with a 3-jaw chuck. Mill only for the optional channel (plug op 80)",
    "Gauges": '6" calipers, 0–1" micrometer (.0001"), 1/2–3/4" telescoping gauge, 0.01 g scale',
}

RULES = [
    "<b>Cup first, then its plug.</b> Each plug is turned to its own cup's measured bore + .0005\". "
    "Plugs are not interchangeable.",
    "<b>Never try a plug in its cup.</b> It's a press fit: it goes in once, after the cup is filled.",
    "<b>Keep the metal clean.</b> Brush steel and brass chips off the lathe first. Cut dry or with light oil. "
    "No water-soluble coolant or tapping fluid: dried coolant goes into the melt.",
    "<b>No marker, scribing or stamps</b> on the parts. <b>No files, emery or Scotch-Brite</b>: abrasive grit can "
    "reach the nozzle. Deburr with a hand deburring tool.",
    "<b>The shop's rules come first.</b> Speeds below are starting points for HSS tools; take the staff's word "
    "over this sheet.",
]

# (op, station, operation and setup, tooling, speed and feed, check)
CUP_OPS = [
    ("10", "Band saw", '<b>Done 10/14 (Logan).</b> Saw a 3.000" blank from the bar.', "—", "—",
     '3.000" ± 1/32"'),
    ("20", "Lathe", 'Chuck the blank in the 3-jaw, about 1" out. <b>Face end A</b> (the cup\'s bottom): just '
     'enough to clean it up, about 1/8". Break the outer edge .020" × 45°.',
     "Right-hand turning tool, on center", "1000–1500 rpm. Feed by hand toward the center",
     "Flat, with no pip at the center (a pip means the tool is off center)"),
    ("30", "Lathe", "Flip it: end A in the jaws, about 1\" in. <b>Face end B to length.</b> Measure between cuts. "
     "Break the outer edge .020\" × 45°.",
     "Same", "Same", '<b>Length 2.750" ± .005"</b> (calipers)'),
    ("40", "Lathe, tailstock", "<b>Center drill</b> end B.", "#3 center drill", "1000–1500 rpm",
     'Countersink about 1/4" across'),
    ("50", "Lathe, tailstock", '<b>Drill the pocket Ø1/2", 2.25" deep to full diameter.</b> Touch the drill tip to '
     'the face and zero the quill, then drill to <b>2.40"</b> (2.25" plus the .15" drill point). Back out every '
     '1/2" to clear the chips.',
     '1/2" HSS jobber drill, 118° point', "800–1000 rpm. Light oil",
     'Caliper depth rod at the center reads about 2.40"'),
    ("60", "Lathe, stopped", "<b>Deburr the mouth of the bore</b>: a .015\" break at most, just enough to take the "
     "burr off so the plug starts straight.", "Hand deburring tool", "Spindle stopped",
     "No burr inside the mouth"),
    ("70", "Bench", "<b>Measure the bore</b> within the top 1/2\" (where the plug sits), with the cup at room "
     "temperature. Two readings, 90° apart. <b>Write both and their average on the record sheet</b>: the plug is "
     "made to that number.",
     '1/2–3/4" telescoping gauge, read with the 0–1" micrometer', "—",
     'Readings within .0005" of each other; if not, measure again and note it'),
    ("80", "Lab", "<b>Clean.</b> Tip out the chips. Flush the bore with 99% IPA from the wash bottle, swab it, and "
     "flush again (heptane or lab detergent first if oil was used). Dry at 80 °C for 30 min before filling.",
     "99% IPA (not 70%), swabs, Kimwipes", "—", "No chips or oil film in the bore"),
    ("90", "Lab", "<b>Weigh and bag.</b> One bag per cup-and-plug set, labelled with the set number, the bore and "
     "the masses. The label goes on the bag, never on the part.", "Scale, 0.01 g", "—",
     "Mass on the record sheet"),
]

PLUG_OPS = [
    ("10", "Bench", "<b>Look up its cup's bore</b> (cup op 70) and write the target on the record sheet: "
     "<b>plug Ø = bore + .0005\"</b>. Anything up to + .0008\" is fine; never more, or the cup wall stretches "
     "for good.", "Record sheet", "—", "Target written down"),
    ("20", "Lathe", "Chuck a 3\" blank, or the stub from the last plug, about 1\" out, with at least 3/4\" in the "
     "jaws. Check whether the cross-slide dial reads diameter or radius. <b>Face the end</b>: it becomes the "
     "nose, which goes in first.",
     "Right-hand turning tool, on center", "1000–1500 rpm", "Flat, no pip at the center"),
    ("30", "Lathe", "<b>Turn the OD to the target</b> over .70\" of length. Rough to about .010\" over, then "
     "take .002\" or less off the diameter per pass, measuring after "
     "each. Let the part cool before the last reading: 10 °C warm reads .0001\" big.",
     "Right-hand turning tool, sharp", "1200–1500 rpm. Rough .005–.010 in/rev, finish .002–.003",
     "<b>Micrometer at both ends of the turned length: bore + .0005\" to + .0008\"</b>, readings within "
     ".0002\" of each other"),
    ("40", "Lathe", "<b>Cut the 15° lead-in on the nose</b>, .060\" long: swivel the compound to feed at 15° to "
     "the spindle axis (on some lathes the scale reads 75° for this) and feed it by hand.",
     "Right-hand turning tool", "About 1000 rpm", "Nose face about .03\" under the OD"),
    ("50", "Lathe, tailstock", "<b>Drill the vent.</b> Spot the center with just the tip of the center drill, then "
     "drill <b>.65\" deep</b>, past where the plug will be parted off. Back out every 1/16\" and clear the "
     "flutes.", "#1 center drill. <b>#60 (.040\") jobber drill</b> (wire-gauge drawer, by the #70)",
     "Top spindle speed. Feed very lightly. Light oil", ".65\" on the tailstock scale"),
    ("60", "Lathe", "<b>Part it off at .5625\"</b>: set the blade's right-hand face .5625\" from the nose face "
     "with the calipers. Steady hand feed. Catch the plug so it can't drop into the chip pan: its OD is the fit.",
     "Parting blade, on center, short stick-out", "400–600 rpm. Light oil",
     "<b>Length .5625\" ± .005\"</b>. Light shows through the vent"),
    ("70", "Bench", "<b>Deburr</b> the edge of the parted face (.015\" break at most) and the vent's exit.",
     "Hand deburring tool", "—", "No burrs. Vent open"),
    ("80", "Mill (optional)", "<b>Compaction (hydraulic-press) plugs only.</b> A channel across the parted face, "
     "through the vent, about .03\" deep, so the vent still breathes under a flat ram. One hacksaw kerf also "
     "works.", "1/16\" end mill, plug in soft jaws",
     "Top speed. Light feed", "Channel crosses the vent"),
    ("90", "Lab", "<b>Clean, weigh and bag</b> as for the cup (cup ops 80 and 90), flushing through the vent too. "
     "Bag it with its own cup. For the next plug, go back to op 10 with the next cup.", "As for the cup", "—",
     "Mass on the record sheet"),
]

RECORD_COLS = [
    "Set", "Cup length<br><small>2.750 ± .005</small>", "Bore depth at center<br><small>2.40</small>",
    "Bore Ø reading 1", "Bore Ø reading 2", "Bore Ø average", "Plug target Ø<br><small>average + .0005</small>",
    "Plug Ø as turned<br><small>both ends</small>", "Plug length<br><small>.5625 ± .005</small>",
    "Cup mass, g", "Plug mass, g", "Made by, date",
]
RECORD_ROWS = 10

VARIANTS = [
    ("Thin-wall cup", "For the 22.5 and 30 wt% points of the 4047 spread. Cup op 50 with a <b>5/8\" drill</b> "
     "(1/2\" first as a pilot), same 2.25\" depth (2.44\" on the quill): a .060\" wall that holds about 16 g. "
     "Its plug is <b>.250\" long</b>, not .5625\", with the same + .0005\" fit."),
    ("Compaction set", "For the hydraulic-press runs. Cup op 50 with a <b>31/64\" drill, then a 1/2\" chucking "
     "reamer</b> to full depth (300–500 rpm, steady feed, light oil; never turn a reamer backwards), so the bore "
     "is smooth and straight. Its plug is a <b>sliding fit</b>, not a press fit, and the clearance isn't decided "
     "yet: ask Sterling before turning one. Then plug op 80."),
]


# ---------------------------------------------------------------- sketches (inline SVG)

def _f(v):
    return f"{v:.1f}"


class Svg:
    def __init__(self, w, h):
        self.w, self.h, self.items = w, h, []

    def add(self, s):
        self.items.append(s)

    def poly(self, pts, fill="none", stroke=INK, sw=1.2, dash=None, extra=""):
        d = " ".join(f"{_f(x)},{_f(y)}" for x, y in pts)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<polygon points="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{da} {extra}/>')

    def line(self, x1, y1, x2, y2, stroke=INK, sw=0.8, dash=None):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{_f(x1)}" y1="{_f(y1)}" x2="{_f(x2)}" y2="{_f(y2)}" stroke="{stroke}" '
                 f'stroke-width="{sw}"{da}/>')

    def text(self, x, y, s, size=10, anchor="start", fill=INK, weight="normal"):
        self.add(f'<text x="{_f(x)}" y="{_f(y)}" font-size="{size}" text-anchor="{anchor}" fill="{fill}" '
                 f'font-weight="{weight}">{html.escape(s)}</text>')

    def arrow(self, x1, y1, x2, y2, stroke=INK2):
        """Line ending in a filled arrowhead at (x2, y2)."""
        self.line(x1, y1, x2, y2, stroke=stroke, sw=0.7)
        a = math.atan2(y2 - y1, x2 - x1)
        k, w = 6.0, 2.2
        p = [(x2, y2), (x2 - k * math.cos(a) + w * math.sin(a), y2 - k * math.sin(a) - w * math.cos(a)),
             (x2 - k * math.cos(a) - w * math.sin(a), y2 - k * math.sin(a) + w * math.cos(a))]
        self.poly(p, fill=stroke, stroke=stroke, sw=0.5)

    def dim_h(self, x1, x2, y, label, ext_from=None):
        """Horizontal dimension at height y between x1 and x2, extension lines up/down from ext_from."""
        if ext_from is not None:
            for x, y0 in zip((x1, x2), ext_from):
                self.line(x, y0, x, y + (3 if y > y0 else -3), stroke=INK2, sw=0.5)
        self.arrow((x1 + x2) / 2, y, x1, y)
        self.arrow((x1 + x2) / 2, y, x2, y)
        self.text((x1 + x2) / 2, y - 3, label, size=9.5, anchor="middle", fill=INK2)

    def balloon(self, x, y, num, tx, ty):
        """Op-number balloon at (x, y), its leader ending in a dot on the feature at (tx, ty)."""
        r = 9 if len(num) < 3 else 10.5
        a = math.atan2(ty - y, tx - x)
        self.line(x + r * math.cos(a), y + r * math.sin(a), tx, ty, stroke=ACCENT, sw=0.8)
        self.add(f'<circle cx="{_f(tx)}" cy="{_f(ty)}" r="1.8" fill="{ACCENT}"/>')
        self.add(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{r}" fill="white" stroke="{ACCENT}" stroke-width="1.2"/>')
        self.text(x, y + 3.4, num, size=9 if len(num) < 3 else 8, anchor="middle", fill=ACCENT, weight="bold")

    def render(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" '
                f'height="{self.h}" font-family="DejaVu Sans, Arial, sans-serif">'
                '<defs><pattern id="hatch" width="5" height="5" patternUnits="userSpaceOnUse" '
                'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="5" stroke="#9a978f" '
                'stroke-width="0.7"/></pattern></defs>' + "".join(self.items) + "</svg>")


def cup_sketch():
    """Sectioned cup, open end B on the right, with the op that makes each feature."""
    s = 118.0  # px per inch
    L, R, rb, depth, c = 2.750, 0.375, 0.25, 2.25, 0.020
    tip = rb / math.tan(math.radians(59))  # .150" drill point
    g = Svg(470, 182)
    x0, y0 = 78, 84
    X = lambda z: x0 + z * s  # noqa: E731
    Y = lambda r: y0 - r * s  # noqa: E731
    shoulder = L - depth
    g.poly([(X(0), Y(R - c)), (X(c), Y(R)), (X(L - c), Y(R)), (X(L), Y(R - c)), (X(L), Y(-R + c)),
            (X(L - c), Y(-R)), (X(c), Y(-R)), (X(0), Y(-R + c))], fill="url(#hatch)", sw=1.3)
    g.poly([(X(L), Y(rb)), (X(shoulder), Y(rb)), (X(shoulder - tip), Y(0)), (X(shoulder), Y(-rb)),
            (X(L), Y(-rb))], fill="white", sw=1.3)
    g.line(X(-0.12), y0, X(L + 0.12), y0, stroke=INK2, sw=0.6, dash="10 3 2 3")
    g.text(X(0) - 6, y0 + 4, "A", size=12, anchor="end", weight="bold")
    g.text(X(L) + 6, y0 + 4, "B", size=12, weight="bold")
    g.text(X(0) - 8, Y(R) + 4, 'Ø.750"', size=9.5, anchor="end", fill=INK2)
    g.text(X(0) - 8, Y(R) + 14, "as bought", size=8.5, anchor="end", fill=INK2)
    g.dim_h(X(shoulder), X(L), Y(R) - 16, '2.25" to full Ø', ext_from=(Y(rb), Y(R)))
    g.dim_h(X(0), X(L), Y(-R) + 32, '2.750"', ext_from=(Y(-R), Y(-R)))
    g.text(X(shoulder) + 8, y0 + 20, 'Ø1/2" drill, 118° point', size=9.5, fill=INK2)
    g.balloon(X(0) - 24, y0 + 32, "20", X(0), Y(-0.16))
    g.balloon(X(L) + 30, y0 - 34, "30", X(L), Y(0.33))
    g.balloon(X(L) + 30, y0 + 34, "60", X(L - 0.01), Y(-rb - 0.01))
    g.balloon(X(0.9), y0 + 60, "50", X(0.9), Y(-rb))
    g.balloon(X(L) - 34, y0 - 4, "70", X(L - 0.22), Y(rb))
    g.text(X(L) - 34, y0 + 18, "measure here", size=8, anchor="middle", fill=ACCENT)
    return g.render()


def plug_sketch():
    """The plug on the end of the blank, before parting: nose on the right, stock running into the chuck."""
    s = 160.0
    R, r, lead_l, L, turned, vent, vent_depth = 0.375, 0.254, 0.060, 0.5625, 0.70, 0.020, 0.65
    lead_r = lead_l * math.tan(math.radians(15))
    blade = 0.094
    g = Svg(470, 182)
    xn, y0 = 300, 90  # nose face, axis
    X = lambda z: xn - z * s  # noqa: E731  (z measured from the nose face toward the chuck)
    Y = lambda rr: y0 - rr * s  # noqa: E731
    zl = 1.0  # where the drawing breaks off, toward the chuck
    g.poly([(X(zl), Y(R)), (X(turned), Y(R)), (X(turned), Y(r)), (X(lead_l), Y(r)), (X(0), Y(r - lead_r)),
            (X(0), Y(-r + lead_r)), (X(lead_l), Y(-r)), (X(turned), Y(-r)), (X(turned), Y(-R)), (X(zl), Y(-R))],
           fill="url(#hatch)", sw=1.3)
    g.line(X(zl), Y(R) - 4, X(zl), Y(-R) + 4, stroke=INK2, sw=0.9, dash="4 3")
    g.text(X(zl) - 5, y0 + 4, "chuck", size=8.5, anchor="end", fill=INK2)
    tip = vent / math.tan(math.radians(59))
    g.poly([(X(0), Y(vent)), (X(vent_depth), Y(vent)), (X(vent_depth + tip), Y(0)), (X(vent_depth), Y(-vent)),
            (X(0), Y(-vent))], fill="white", sw=1.0)
    g.line(X(zl), y0, X(-0.1), y0, stroke=INK2, sw=0.6, dash="10 3 2 3")
    g.poly([(X(L), Y(R) - 8), (X(L + blade), Y(R) - 8), (X(L + blade), Y(-R) + 8), (X(L), Y(-R) + 8)],
           fill="#2a78d61f", stroke=ACCENT, sw=0.8, dash="3 2")
    g.text(X(L + blade) - 4, Y(R) - 12, "part line", size=8.5, anchor="end", fill=ACCENT)
    g.dim_h(X(L), X(0), Y(-R) + 22, '.5625"', ext_from=(Y(-r), Y(-r + lead_r)))
    g.balloon(X(0.30), Y(R) - 16, "30", X(0.30), Y(r))
    g.text(X(0.30) + 14, Y(R) - 12, 'Ø = its cup\'s bore + .0005"', size=9.5, fill=INK2)
    g.balloon(X(L) + 10, Y(R) - 16, "60", X(L), Y(r) - 1)
    for yy, num, target, label in ((y0 - 30, "20", (X(0), y0 - 16), "face: the nose, goes in first"),
                                   (y0, "50", (X(0.12), y0), '#60 vent, .65" deep'),
                                   (y0 + 30, "40", (X(0.025), Y(-r + lead_r * 0.5)), '15° × .060" lead-in')):
        g.balloon(X(0) + 26, yy, num, *target)
        g.text(X(0) + 40, yy + 3.5, label, size=9.5, fill=INK2)
    g.balloon(X(L) + 14, Y(-R) + 22, "70", X(L) + 0.5, Y(-r) + 0.5)
    return g.render()


# ---------------------------------------------------------------- pages

CSS = f"""
@page {{ size: 11in 8.5in; margin: 0.35in 0.4in; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: "DejaVu Sans Condensed", "DejaVu Sans", Arial, sans-serif; color: {INK};
        font-size: 8.4pt; }}
.page {{ height: 7.78in; display: flex; flex-direction: column; page-break-after: always; overflow: hidden; }}
.page:last-child {{ page-break-after: auto; }}
.top {{ display: flex; justify-content: space-between; align-items: baseline;
        border-bottom: 2px solid {INK}; padding-bottom: 3px; }}
h1 {{ font-size: 15pt; margin: 0; }}
.meta {{ font-size: 8pt; color: {INK2}; text-align: right; }}
.info {{ display: grid; grid-template-columns: 0.75in 1fr 0.75in 1fr; gap: 1px 8px; margin: 5px 0 4px;
         font-size: 8.2pt; }}
.info b {{ color: {INK2}; font-weight: normal; }}
.band {{ display: flex; gap: 14px; align-items: flex-start; margin: 2px 0 6px; }}
.band svg {{ flex: none; }}
.rules {{ flex: 1; font-size: 8.2pt; }}
h2 {{ font-size: 9pt; margin: 2px 0 3px; text-transform: uppercase; letter-spacing: .04em;
                     color: {INK2}; }}
.rules ol {{ margin: 0; padding-left: 15px; }}
.rules li {{ margin-bottom: 2px; }}
table {{ border-collapse: collapse; width: 100%; }}
.ops th {{ background: {SECTION}; text-align: left; font-size: 8pt; padding: 3px 5px; border: 1px solid {RULE}; }}
.ops td {{ vertical-align: top; padding: 2px 5px; border: 1px solid {RULE}; line-height: 1.22; }}
.ops td.op {{ font-weight: bold; text-align: center; width: 0.38in; font-size: 9.5pt; }}
.ops td.st {{ width: 0.85in; color: {INK2}; }}
.ops td.tool {{ width: 1.5in; }}
.ops td.spd {{ width: 1.35in; }}
.ops td.chk {{ width: 1.85in; }}
.ops td.done {{ color: {INK2}; }}
.rec th {{ background: {SECTION}; font-size: 7.8pt; padding: 3px 3px; border: 1px solid {INK2}; line-height: 1.2; }}
.rec th small {{ font-weight: normal; color: {INK2}; }}
.rec td {{ border: 1px solid {INK2}; height: 0.42in; text-align: center; font-weight: bold; }}
.variants {{ margin-top: 8px; display: grid; grid-template-columns: 1.15in 1fr; gap: 3px 10px; font-size: 8.4pt; }}
.variants .k {{ font-weight: bold; }}
.foot {{ margin-top: auto; font-size: 7.5pt; color: {INK2}; border-top: 1px solid {RULE}; padding-top: 3px;
         display: flex; justify-content: space-between; }}
"""


def ops_table(ops):
    rows = []
    for op, st, what, tool, spd, chk in ops:
        cls = ' class="done"' if what.startswith("<b>Done") else ""
        rows.append(f'<tr><td class="op">{op}</td><td class="st">{st}</td><td{cls}>{what}</td>'
                    f'<td class="tool">{tool}</td><td class="spd">{spd}</td><td class="chk">{chk}</td></tr>')
    return ('<table class="ops"><tr><th>Op</th><th>Station</th><th>Operation and setup</th><th>Tooling</th>'
            "<th>Speed, feed</th><th>Check</th></tr>" + "".join(rows) + "</table>")


def info_grid(part, qty):
    cells = [("Part", part), ("Quantity", qty), ("Material", HEADER["Material"]), ("Stock", HEADER["Stock"]),
             ("Machines", HEADER["Machines"]), ("Gauges", HEADER["Gauges"])]
    return '<div class="info">' + "".join(f"<b>{k}</b><span>{v}</span>" for k, v in cells) + "</div>"


def page(title, part, qty, sketch, ops, n):
    rules = "".join(f"<li>{r}</li>" for r in RULES)
    return f"""<div class="page">
<div class="top"><h1>{title}</h1><div class="meta">Rev {REV} · {DATE} · page {n} of 3</div></div>
{info_grid(part, qty)}
<div class="band">{sketch}<div class="rules"><h2>Rules for every part</h2><ol>{rules}</ol></div></div>
{ops_table(ops)}
<div class="foot"><span>byu-vcl · atomizer-charge/process-sheet · sizes as made (#222), restated in PR #277</span>
<span>Balloons in the sketch are op numbers</span></div>
</div>"""


def record_page():
    head = "".join(f"<th>{c}</th>" for c in RECORD_COLS)
    body = "".join("<tr>" + f"<td>{i}</td>" + "<td></td>" * (len(RECORD_COLS) - 1) + "</tr>"
                   for i in range(1, RECORD_ROWS + 1))
    variants = "".join(f'<div class="k">{k}</div><div>{v}</div>' for k, v in VARIANTS)
    return f"""<div class="page">
<div class="top"><h1>Record sheet: one row per cup-and-plug set</h1>
<div class="meta">Rev {REV} · {DATE} · page 3 of 3</div></div>
<p style="margin:6px 0 8px;font-size:8.6pt">Fill in the cup's columns first. The plug's target is the cup's average
bore + .0005"; anything up to + .0008" is fine. Bag each plug with its own cup and copy the set number onto the bag.
Inches unless marked. Post a photo of this sheet in PR #277 when the sets are done.</p>
<table class="rec"><tr>{head}</tr>{body}</table>
<h2 style="margin-top:12px">Variants: change only these ops</h2>
<div class="variants">{variants}</div>
<div class="foot"><span>byu-vcl · atomizer-charge/process-sheet</span><span>{PR}</span></div>
</div>"""


def build_html():
    pages = [
        page("Process sheet: Al charge cup", "Standard cup (P2), as made", "One cup per 3\" blank",
             cup_sketch(), CUP_OPS, 1),
        page("Process sheet: Al charge plug", "Plug for the standard cup (P3), as made",
             "Two plugs per 3\" blank, each matched to one cup", plug_sketch(), PLUG_OPS, 2),
        record_page(),
    ]
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>' + \
        "".join(pages) + "</body></html>"


def print_pdf(html_text):
    chrome = os.environ.get("CHROME") or next(
        (p for p in ("google-chrome", "chromium", "chromium-browser") if shutil.which(p)), None)
    if chrome is None:
        raise SystemExit("needs Chrome or Chromium to print the PDF; set CHROME")
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "sheet.html"
        src.write_text(html_text, encoding="utf-8")
        subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                        f"--print-to-pdf={PDF}", src.as_uri()], check=True, capture_output=True)


def write_pngs(dpi=150):
    import pymupdf

    doc = pymupdf.open(PDF)
    for i, pg in enumerate(doc, start=1):
        pg.get_pixmap(dpi=dpi).save(HERE / f"process_sheet-p{i}.png")
    return doc.page_count


# ---------------------------------------------------------------- markdown twin

def _md(s):
    s = re.sub(r"<br>\s*<small>(.*?)</small>", r" (\1)", s)
    s = s.replace("<b>", "**").replace("</b>", "**")
    return re.sub(r"<[^>]+>", "", s).replace("|", "\\|")


def build_md():
    out = ["# Process sheets: Al charge cup and plug", "",
           f"Generated by [`process_sheet.py`](process_sheet.py), rev {REV}, {DATE}. Print "
           "[`process_sheet.pdf`](process_sheet.pdf) (Letter, landscape) for the shop; this page is the same "
           "content for reading on a phone.", ""]
    out += [f"- **{k}:** {v}" for k, v in HEADER.items()] + ["", "## Rules for every part", ""]
    out += [f"{i}. {_md(r)}" for i, r in enumerate(RULES, 1)]
    for title, ops, png in (("Cup (P2, as made): one per 3\" blank", CUP_OPS, "process_sheet-p1.png"),
                            ("Plug (P3, as made): two per 3\" blank", PLUG_OPS, "process_sheet-p2.png")):
        out += ["", f"## {title}", "", f"![]({png})", "",
                "| Op | Station | Operation and setup | Tooling | Speed, feed | Check |", "|---|---|---|---|---|---|"]
        out += [f"| {op} | {_md(st)} | {_md(w)} | {_md(t)} | {_md(sp)} | {_md(c)} |"
                for op, st, w, t, sp, c in ops]
    out += ["", "## Record sheet", "", "Page 3 of the PDF: one row per set, carrying each cup's bore over to its "
            "plug. Columns: " + "; ".join(_md(c) for c in RECORD_COLS) + ".", "",
            "## Variants: change only these ops", ""]
    out += [f"- **{k}.** {_md(v)}" for k, v in VARIANTS]
    return "\n".join(out) + "\n"


def main():
    print_pdf(build_html())
    n = write_pngs()
    MD.write_text(build_md(), encoding="utf-8")
    print(f"wrote {PDF.name} ({n} pages), {n} PNGs, {MD.name}")


if __name__ == "__main__":
    main()

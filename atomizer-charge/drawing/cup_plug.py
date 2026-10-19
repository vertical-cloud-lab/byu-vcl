"""Shop drawing of the charge cup and its plug, at the sizes they were made (#222, #248, PR #277).

PR #232's drawing (atomizer-charge/cad/drawings/charge_parts.pdf) is the design: a 2.500" cup
1.875" deep and a .375" plug.  The cups and plugs actually made are Gage's 2.750" cup with a
1/2" drill 2.25" deep and Ronnie's .5625" plug with a #60 vent, and new ones are made to match
them, so this sheet follows those.  One US-Letter landscape sheet, third-angle projection,
inches with [mm].  Printed at 100 %, the cup is 1:1 and the plug 3:1.  How to make them (order
of operations, tools, speeds, record sheet) is in ../process-sheet/, which this sheet agrees with.

Usage:  python cup_plug.py      (writes cup_plug.pdf and cup_plug.png next to it)
"""

from __future__ import annotations

import math
import pathlib
import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Rectangle

HERE = pathlib.Path(__file__).resolve().parent
MM = 25.4

# ---------------------------------------------------------------------------
# Sizes, inches.  As made unless the comment says otherwise.
# ---------------------------------------------------------------------------
STOCK_D = 0.750  # McMaster 1640T16, 6063-T52; OD left as received (+/-.014")
BLANK_L = 3.000  # the sawn blanks (#277, Oct 14)
CUP_L = 2.750  # Gage, #222: both ends faced
BORE_D = 0.500  # 1/2" drill
DEPTH = 2.25  # Gage, #222: "2.25 in (cone-shaped end)".  To full diameter, as in #232's CAD, the
# drawing convention and ../process-sheet/: the point goes on to 2.40.  Nobody recorded which way the
# first cups were measured; to the point would be .15 shallower, ~0.8 g less powder room.
POINT_DEG = 118.0  # general-purpose drill point
PLUG_L = 0.5625  # Ronnie, #222
FIRST_PLUG_D = 0.508  # the first plugs, turned for their own cups: a reference, not a size to reuse
FIT = (0.0005, 0.0008)  # plug over its cup's measured bore.  Aim for the low end: at .0008 the
# .12" wall is near yield in von Mises (#232, Oct 7, composition_spread notes)
VENT_D = 0.040  # #60 wire-gauge drill
LEADIN_DEG, LEADIN_L = 15.0, 0.060  # nose lead-in, #232 design (charge_cad.py)
PLUG_CHAMFER = 0.015  # break on the parted (top) face, #232
RIM_CHAMFER = 0.015  # bore entrance, so the plug starts square, #232
EDGE_CHAMFER = 0.020  # outside edges, #232
CHANNEL_W, CHANNEL_DEPTH = 0.047, 0.031  # optional, press runs: 1.2 x 0.8 mm, as in the clips
THIN_BORE_D, THIN_PLUG_L = 0.625, 0.250  # thin-wall cup and its plug (composition_spread.py, #232)
RHO_6063 = 2.69  # g/cm^3

CUP_SCALE, PLUG_SCALE = 1.0, 3.0


def point_h(d: float) -> float:
    """Length of the cone a drill of diameter d leaves at the bottom of the hole."""
    return (d / 2) / math.tan(math.radians(POINT_DEG / 2))


def cup_mass_g(bore: float, depth: float = DEPTH) -> float:
    """6063 cup, nominal stock, bore to depth at full diameter plus the point; chamfers ignored."""
    hole = math.pi * (bore / 2) ** 2 * (depth + point_h(bore) / 3)
    return (math.pi * (STOCK_D / 2) ** 2 * CUP_L - hole) * MM**3 / 1000 * RHO_6063


def plug_mass_g(d: float, length: float) -> float:
    return math.pi / 4 * (d**2 - VENT_D**2) * length * MM**3 / 1000 * RHO_6063


# ---------------------------------------------------------------------------
# Profiles in part coordinates: x along the axis, y radial (+ above the axis)
# ---------------------------------------------------------------------------
def cup_outline(bore=BORE_D):
    """The cut face of the cup: one U-shaped region, open end at x = CUP_L."""
    R, r, c, rc = STOCK_D / 2, bore / 2, EDGE_CHAMFER, RIM_CHAMFER
    x_full, x_apex = CUP_L - DEPTH, CUP_L - DEPTH - point_h(bore)
    top = [(0, R - c), (c, R), (CUP_L - c, R), (CUP_L, R - c), (CUP_L, r + rc), (CUP_L - rc, r), (x_full, r)]
    return top + [(x_apex, 0)] + [(x, -y) for x, y in reversed(top)]


def plug_halves(d=FIRST_PLUG_D, length=PLUG_L):
    """The plug's cut face is two regions, either side of the vent.  Nose at x = 0."""
    r, rv, pc = d / 2, VENT_D / 2, PLUG_CHAMFER
    li_r = LEADIN_L * math.tan(math.radians(LEADIN_DEG))
    upper = [(0, rv), (0, r - li_r), (LEADIN_L, r), (length - pc, r), (length, r - pc), (length, rv)]
    return upper, [(x, -y) for x, y in upper]


# ---------------------------------------------------------------------------
# Drafting
# ---------------------------------------------------------------------------
INK = "#000000"
GREY = "#555555"
AIR = "#1f6fd1"
THICK, THIN = 1.1, 0.45  # pt
FS = 7.0  # dimension text, pt
GAP, OVER = 0.04, 0.07  # extension lines: gap from the part, overshoot past the dimension line
CENTRE = (0, (16, 3, 4, 3))
PHANTOM = (0, (14, 3, 3, 3, 3, 3))
plt.rcParams.update({"font.family": "DejaVu Sans", "hatch.linewidth": 0.35, "lines.scale_dashes": False,
                     "pdf.fonttype": 42})


class View:
    """Places part coordinates (inches) on the page at a scale, axis horizontal."""

    def __init__(self, ax, x0, yc, scale):
        self.ax, self.x0, self.yc, self.s = ax, x0, yc, scale

    def p(self, x, y):
        return self.x0 + x * self.s, self.yc + y * self.s

    def section(self, outline, hatch="//////", z=2):
        pts = [self.p(x, y) for x, y in outline]
        self.ax.add_patch(Polygon(pts, closed=True, fill=False, hatch=hatch, lw=0, edgecolor=GREY, zorder=z))
        self.ax.add_patch(Polygon(pts, closed=True, fill=False, lw=THICK, edgecolor=INK, joinstyle="miter",
                                  zorder=z + 1))

    def line(self, pts, **kw):
        line(self.ax, [self.p(x, y) for x, y in pts], **kw)

    def axis(self, x1, x2):
        self.line([(x1 - 0.12 / self.s, 0), (x2 + 0.12 / self.s, 0)], ls=CENTRE)


def line(ax, pts, lw=THIN, ls="-", color=INK, z=4):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, lw=lw, ls=ls, color=color, solid_capstyle="butt", dash_capstyle="butt", zorder=z)


def arrowhead(ax, tip, direction, length=0.10, color=INK):
    dx, dy = direction
    n = math.hypot(dx, dy)
    dx, dy = dx / n, dy / n
    w = length / 6
    bx, by = tip[0] - dx * length, tip[1] - dy * length
    ax.add_patch(Polygon([tip, (bx - dy * w, by + dx * w), (bx + dy * w, by - dx * w)], closed=True,
                         fc=color, ec=color, lw=0.2, zorder=6))


def label(ax, x, y, s, ha="center", va="center", fs=FS, color=INK, box=True, **kw):
    bbox = dict(boxstyle="square,pad=0.12", fc="white", ec="none") if box else None
    return ax.text(x, y, s, ha=ha, va=va, fontsize=fs, color=color, linespacing=1.3, bbox=bbox, zorder=7, **kw)


def hdim(ax, a, b, y, text):
    """Horizontal dimension between page points a and b, its line at height y, text in a break."""
    for x, yf in (a, b):
        s = 1 if y > yf else -1
        line(ax, [(x, yf + s * GAP), (x, y + s * OVER)])
    line(ax, [(a[0], y), (b[0], y)])
    arrowhead(ax, (a[0], y), (-1, 0))
    arrowhead(ax, (b[0], y), (1, 0))
    label(ax, (a[0] + b[0]) / 2, y, text)


def vdim(ax, a, b, x, text, side="left"):
    """Vertical dimension between page points a and b, its line at x; text beside it, horizontal."""
    for xf, y in (a, b):
        s = 1 if x > xf else -1
        line(ax, [(xf + s * GAP, y), (x + s * OVER, y)])
    line(ax, [(x, a[1]), (x, b[1])])
    up = 1 if b[1] > a[1] else -1
    arrowhead(ax, (x, a[1]), (0, -up))
    arrowhead(ax, (x, b[1]), (0, up))
    off = -0.07 if side == "left" else 0.07
    label(ax, x + off, (a[1] + b[1]) / 2, text, ha="right" if side == "left" else "left", box=False)


def leader(ax, target, text_xy, text, ha="left", fs=FS, color=INK):
    """Leader from a shoulder at the note's first line (feature above) or last line (feature below)."""
    tx, ty = text_xy
    sx = tx - 0.05 if ha == "left" else tx + 0.05
    knee = (sx - 0.13, ty) if ha == "left" else (sx + 0.13, ty)
    line(ax, [(sx, ty), knee, target], color=color)
    arrowhead(ax, target, (target[0] - knee[0], target[1] - knee[1]), color=color)
    if "\n" not in text:
        label(ax, tx, ty, text, ha=ha, fs=fs, color=color, box=False)
    elif target[1] < ty:
        label(ax, tx, ty - 0.055, text, ha=ha, va="bottom", fs=fs, color=color, box=False)
    else:
        label(ax, tx, ty + 0.055, text, ha=ha, va="top", fs=fs, color=color, box=False)


def cutting_plane(ax, cx, cy, half, letter):
    """Cutting-plane trace through an end view: vertical, arrows to the right (the direction of sight
    of a section placed to the left, third angle)."""
    y0, y1 = cy - half, cy + half
    line(ax, [(cx, y0), (cx, y1)], lw=THICK, ls=PHANTOM)
    for y in (y0, y1):
        line(ax, [(cx, y), (cx + 0.16, y)], lw=THICK)
        arrowhead(ax, (cx + 0.26, y), (1, 0), length=0.11)
        label(ax, cx - 0.09, y, letter, fs=9, box=False, weight="bold")


def end_cross(ax, cx, cy, r):
    line(ax, [(cx - r - 0.12, cy), (cx + r + 0.12, cy)], ls=CENTRE)
    line(ax, [(cx, cy - r - 0.12), (cx, cy + r + 0.12)], ls=CENTRE)


def circle(ax, cx, cy, r, lw=THICK, ls="-", color=INK):
    ax.add_patch(Circle((cx, cy), r, fill=False, lw=lw, ls=ls, edgecolor=color, zorder=4))


def view_title(ax, x, y, title, sub):
    ax.text(x, y, title, ha="center", va="top", fontsize=9, weight="bold", color=INK)
    ax.text(x, y - 0.17, sub, ha="center", va="top", fontsize=6.6, color=GREY)


def third_angle_symbol(ax, x, y, h=0.12):
    """ASME Y14.3 third-angle symbol: end view on the left, the frustum pointing at it on the right."""
    circle(ax, x, y, h / 2, lw=0.6)
    circle(ax, x, y, h / 4, lw=0.6)
    xl, xr = x + h * 0.95, x + h * 0.95 + h * 1.2
    ax.add_patch(Polygon([(xl, y - h / 4), (xr, y - h / 2), (xr, y + h / 2), (xl, y + h / 4)], closed=True,
                         fill=False, lw=0.6, edgecolor=INK, zorder=4))
    line(ax, [(x - h * 0.7, y), (xr + h * 0.3, y)], lw=0.3, ls=CENTRE)


def fin(d: float, places: int = 3) -> str:
    return f"{d:.{places}f}".lstrip("0")


# ---------------------------------------------------------------------------
# The sheet
# ---------------------------------------------------------------------------
def draw_cup(ax):
    R, r = STOCK_D / 2, BORE_D / 2
    v = View(ax, 1.70, 6.40, CUP_SCALE)
    v.section(cup_outline())
    x_full = CUP_L - DEPTH
    for x in (x_full, CUP_L - RIM_CHAMFER):  # circular edges seen inside the bore, beyond the cut
        v.line([(x, -r), (x, r)], lw=THICK * 0.75)
    v.axis(0, CUP_L)
    left, right, top, bottom = v.p(0, 0)[0], v.p(CUP_L, 0)[0], v.p(0, R)[1], v.p(0, -R)[1]

    hdim(ax, v.p(0, -R), v.p(CUP_L, -R), bottom - 0.32, f"{fin(CUP_L)} [{CUP_L * MM:.2f}]")
    vdim(ax, v.p(0.0, -R), v.p(0.0, R), left - 0.30, f"Ø{fin(STOCK_D)} [{STOCK_D * MM:.2f}]\n"
         "STOCK, AS RECEIVED")
    leader(ax, v.p(1.55, r), (left + 0.55, top + 0.40),
           f"Ø{fin(BORE_D)} (1/2) DRILL, {DEPTH:.2f} [{DEPTH * MM:.2f}] DEEP TO FULL Ø\n"
           f"{POINT_DEG:.0f}° POINT REACHES {DEPTH + point_h(BORE_D):.2f}  ·  MEASURE THE BORE: NOTE 2")
    leader(ax, v.p(CUP_L - RIM_CHAMFER / 2, r + RIM_CHAMFER / 2), (right + 0.24, top + 0.14),
           f"{fin(RIM_CHAMFER)} × 45° MAX\nBORE MOUTH")
    leader(ax, v.p(EDGE_CHAMFER / 2, -R + EDGE_CHAMFER / 2), (left - 0.62, bottom - 0.30),
           f"{fin(EDGE_CHAMFER)} × 45°\nBOTH ENDS", ha="right")
    label(ax, left - 0.08, top + 0.14, "BOTTOM", fs=6.2, color=GREY, box=False, ha="right")
    label(ax, right + 0.10, bottom - 0.05, "OPEN END", fs=6.2, color=GREY, box=False, ha="left")

    # End view, looking into the open end
    cx, cy = right + 1.25, v.yc
    for rr, lw in ((R, THICK), (R - EDGE_CHAMFER, THICK * 0.75), (r + RIM_CHAMFER, THICK * 0.75), (r, THICK)):
        circle(ax, cx, cy, rr * CUP_SCALE, lw=lw)
    end_cross(ax, cx, cy, R * CUP_SCALE)
    cutting_plane(ax, cx, cy, R * CUP_SCALE + 0.24, "A")
    ax.text(cx, cy - R - 0.42, "END VIEW", ha="center", va="top", fontsize=6.6, color=GREY)

    view_title(ax, (left + right) / 2, bottom - 0.55, "CUP (P2)  ·  SECTION A-A  ·  1:1",
               f"FROM A {fin(BLANK_L)} BLANK: FACE ABOUT .125 OFF EACH END")


def draw_plug(ax):
    s = PLUG_SCALE
    r = FIRST_PLUG_D / 2
    v = View(ax, 2.05, 3.70, s)
    for half in plug_halves():
        v.section(half, hatch="\\\\\\\\\\\\")
    v.axis(0, PLUG_L)
    # optional channel across the top face: phantom, it's only for the press runs
    hw = CHANNEL_W / 2
    v.line([(PLUG_L, hw), (PLUG_L - CHANNEL_DEPTH, hw), (PLUG_L - CHANNEL_DEPTH, -hw), (PLUG_L, -hw)],
           lw=0.7, ls=PHANTOM)
    left, right, top, bottom = v.p(0, 0)[0], v.p(PLUG_L, 0)[0], v.p(0, r)[1], v.p(0, -r)[1]

    li_r = LEADIN_L * math.tan(math.radians(LEADIN_DEG))
    hdim(ax, v.p(0, -r + li_r), v.p(PLUG_L, -r + PLUG_CHAMFER), bottom - 0.32,
         f"{fin(PLUG_L, 4)} ±.005 [{PLUG_L * MM:.2f}]")
    lo, hi = FIT
    vdim(ax, v.p(LEADIN_L + 0.03, -r), v.p(LEADIN_L + 0.03, r), left - 0.30,
         f"Ø = ITS OWN CUP'S BORE\n+{fin(lo, 4)} (+{fin(hi, 4)} MAX)\n"
         f"THE FIRST ONES: Ø{fin(FIRST_PLUG_D)},\nFOR THEIR CUPS. MEASURE!")
    leader(ax, v.p(LEADIN_L / 2, -r + li_r / 2), (left - 0.50, bottom - 0.24),
           f"{fin(LEADIN_L)} × {LEADIN_DEG:.0f}° LEAD-IN\n(TAPER THE NOSE)", ha="right")
    leader(ax, v.p(PLUG_L - PLUG_CHAMFER / 2, r - PLUG_CHAMFER / 2), (right + 0.16, top + 0.26),
           f"{fin(PLUG_CHAMFER)} × 45° MAX")
    label(ax, left - 0.08, top + 0.16, "NOSE: GOES IN FIRST", fs=6.2, color=GREY, box=False, ha="right")
    label(ax, right + 0.10, bottom - 0.06, "TOP: THE PARTED FACE", fs=6.2, color=GREY, box=False, ha="left")

    # End view, looking at the top face
    cx, cy = right + 1.70, v.yc
    circle(ax, cx, cy, r * s)
    circle(ax, cx, cy, (r - PLUG_CHAMFER) * s, lw=THICK * 0.75)
    circle(ax, cx, cy, VENT_D / 2 * s)
    end_cross(ax, cx, cy, r * s)
    xe = math.sqrt(r**2 - hw**2) * s
    for y in (hw, -hw):
        line(ax, [(cx - xe, cy + y * s), (cx + xe, cy + y * s)], lw=0.7, ls=PHANTOM)
    cutting_plane(ax, cx, cy, r * s + 0.24, "B")
    ax.text(cx, cy - r * s - 0.37, "END VIEW: THE TOP FACE", ha="center", va="top", fontsize=6.6, color=GREY)
    a = math.radians(125)
    leader(ax, (cx + VENT_D / 2 * s * math.cos(a), cy + VENT_D / 2 * s * math.sin(a)),
           (cx - 0.70, cy + r * s + 0.60), f"#60 (Ø{fin(VENT_D)}) THRU, ON CENTER\nTHE AIR VENT (NOTE 5)")
    leader(ax, (cx + xe * 0.55, cy - hw * s), (cx + 0.92, cy - r * s - 0.68),
           "OPTIONAL, PRESS RUNS ONLY (NOTE 8):\n"
           f"CHANNEL ≈{fin(CHANNEL_DEPTH, 2)} DEEP ACROSS THE TOP, THROUGH\n"
           "THE VENT: ONE HACKSAW KERF OR 1/16 END MILL", ha="right")

    view_title(ax, (left + right) / 2 - 0.10, bottom - 0.55, "PLUG (P3)  ·  SECTION B-B  ·  3:1",
               "ONE PER CUP, MADE AFTER ITS CUP")


def draw_assembly(ax):
    """The pair as it goes in the crucible: plug pressed flush, powder under it.  Reference only."""
    R, r = STOCK_D / 2, BORE_D / 2
    v = View(ax, 6.75, 6.40, 1.0)
    v.section(cup_outline())
    x_nose = CUP_L - PLUG_L
    x_full, x_apex = CUP_L - DEPTH, CUP_L - DEPTH - point_h(BORE_D)
    powder = [(x_apex, 0), (x_full, r), (x_nose, r), (x_nose, -r), (x_full, -r)]
    pts = [v.p(x, y) for x, y in powder]
    ax.add_patch(Polygon(pts, closed=True, fc="#f1ede4", hatch="....", lw=0, edgecolor="#9a8f78", zorder=2))
    for half in plug_halves(d=BORE_D):
        v.section([(x + x_nose, y) for x, y in half], hatch="\\\\\\\\\\\\")
    v.axis(0, CUP_L)
    left, top, bottom = v.p(0, 0)[0], v.p(0, R)[1], v.p(0, -R)[1]
    tip = v.p(CUP_L + 0.42, 0)
    line(ax, [v.p(x_nose + 0.05, 0), tip], lw=1.0, color=AIR, z=8)
    arrowhead(ax, tip, (1, 0), color=AIR)
    label(ax, tip[0] + 0.05, tip[1], "AIR OUT", ha="left", fs=6.4, color=AIR, box=False)
    leader(ax, v.p(x_nose + 0.30, r - 0.05), (v.p(x_nose, 0)[0] - 0.55, top + 0.32),
           "PLUG PRESSED FLUSH, NOSE IN", ha="right")
    leader(ax, v.p(1.10, -0.12), (left + 0.25, bottom - 0.28), "POWDER, WEIGHED AND TAPPED DOWN")
    view_title(ax, v.p(CUP_L / 2, 0)[0], bottom - 0.55, "ASSEMBLED AND FILLED  ·  REF  ·  1:1",
               "STANDS PLUG-UP IN THE CRUCIBLE")


NOTES = [
    "MATERIAL: 6063-T52 ALUMINUM ROD, Ø3/4 (McMASTER 1640T16), FROM THE 3.000 SAWN BLANKS. LEAVE THE OD AS "
    "RECEIVED.",
    "MAKE THE CUP FIRST. MEASURE ITS BORE IN THE TOP 1/2 WITH A TELESCOPING GAGE AND A MICROMETER, TWICE, "
    "90° APART, AND TURN ITS PLUG TO THE AVERAGE +.0005. NEVER OVER +.0008: A TIGHTER PLUG PERMANENTLY "
    "STRETCHES THE CUP WALL.",
    "ONE PLUG PER CUP: THEY ARE NOT INTERCHANGEABLE, AND A PLUG GOES INTO ITS CUP ONCE, AFTER FILLING. BAG EACH "
    "PAIR TOGETHER AND LABEL THE BAG. NO MARKER, SCRIBING OR STAMPS ON THE PARTS.",
    "ORDER OF OPERATIONS, TOOLS, SPEEDS AND THE RECORD SHEET: SEE THE PROCESS SHEETS, "
    "atomizer-charge/process-sheet/ (PR #277).",
    "EVERY PLUG GETS THE #60 VENT. THE FURNACE IS PUMPED DOWN BEFORE MELTING, AND WITHOUT A VENT THE AIR UNDER "
    "THE PLUG HAS TO ESCAPE THROUGH THE POWDER.",
    "CUT DRY OR WITH LIGHT OIL. NO WATER-SOLUBLE COOLANT, AND NO FILES, EMERY OR SCOTCH-BRITE: RESIDUE AND GRIT "
    "END UP IN THE MELT. BRUSH STEEL AND BRASS CHIPS OFF THE LATHE FIRST.",
    "FLUSH THE BORE WITH 99% IPA, SWAB IT AND FLUSH AGAIN; DRY AT 80 °C FOR 30 MIN. WEIGH EACH PART TO 0.01 g "
    "AND WRITE THE MASSES ON THE BAG.",
    "HYDRAULIC-PRESS RUNS ONLY: DRILL 31/64, THEN REAM TO .500 SO THE BORE IS STRAIGHT AND SMOOTH, AND CUT THE "
    "CHANNEL. THAT PLUG SLIDES IN RATHER THAN PRESSING IN, AND ITS CLEARANCE ISN'T SET YET: ASK STERLING "
    "BEFORE MAKING ONE.",
]


def draw_notes(ax, x, y_top, width_chars=70):
    ax.text(x, y_top, "NOTES", fontsize=7.6, weight="bold", color=INK, va="top")
    y = y_top - 0.19
    for i, note in enumerate(NOTES, 1):
        for j, ln in enumerate(textwrap.wrap(note, width_chars)):
            if j == 0:
                ax.text(x, y, f"{i}.", fontsize=6.4, color=INK, va="top")
            ax.text(x + 0.17, y, ln, fontsize=6.4, color=INK, va="top")
            y -= 0.108
        y -= 0.03
    return y


def draw_variants(ax, x, y, w):
    rows = [
        ("", "STANDARD, AS MADE (SHOWN)", "THIN WALL"),
        ("FOR", "ALL RUNS SO FAR", "HIGH-POWDER RUNS (#264)"),
        ("CUP BORE", f"Ø{fin(BORE_D)} (1/2) DRILL", f"Ø{fin(THIN_BORE_D)} (5/8) DRILL, AFTER THE 1/2"),
        ("CUP WALL", f"{fin((STOCK_D - BORE_D) / 2)}", f"{fin((STOCK_D - THIN_BORE_D) / 2, 4)}"),
        ("BORE DEPTH", f"{DEPTH:.2f} TO FULL Ø (POINT AT {DEPTH + point_h(BORE_D):.2f})",
         f"{DEPTH:.2f} TO FULL Ø (POINT AT {DEPTH + point_h(THIN_BORE_D):.2f})"),
        ("PLUG LENGTH", f"{fin(PLUG_L, 4)} (9/16)", f"{fin(THIN_PLUG_L)} (1/4)"),
        ("PLUG Ø", f"CUP BORE +{fin(FIT[0], 4)} (+{fin(FIT[1], 4)} MAX)", f"CUP BORE +{fin(FIT[0], 4)}, NO MORE"),
        ("MASS, CUP / PLUG (REF)", f"≈{cup_mass_g(BORE_D):.0f} g / {plug_mass_g(FIRST_PLUG_D, PLUG_L):.1f} g",
         f"≈{cup_mass_g(THIN_BORE_D):.0f} g / {plug_mass_g(THIN_BORE_D, THIN_PLUG_L):.1f} g"),
    ]
    cols = [x, x + 1.45, x + 1.45 + (w - 1.45) * 0.47, x + w]
    rh = 0.165
    ax.text(x, y + 0.08, "TWO VERSIONS: ALL ELSE IS THE SAME", fontsize=7.6, weight="bold",
            color=INK, va="bottom")
    for i, row in enumerate(rows):
        yt = y - i * rh
        for j, cell in enumerate(row):
            ax.text(cols[j] + 0.06, yt - rh / 2, cell, fontsize=6.4, va="center", color=INK,
                    weight="bold" if i == 0 or j == 0 else "normal")
        line(ax, [(x, yt - rh), (x + w, yt - rh)], lw=0.35)
    yb = y - len(rows) * rh
    ax.add_patch(Rectangle((x, yb), w, y - yb, fill=False, lw=0.7, edgecolor=INK, zorder=4))
    for c in cols[1:-1]:
        line(ax, [(c, y), (c, yb)], lw=0.35)
    ax.text(x, yb - 0.07, "MASSES: 6063 AT 2.69 g/cm³, NOMINAL STOCK. THE BAR'S OD TOLERANCE MOVES THEM "
            "ABOUT 4 %.", fontsize=5.8, color=GREY, va="top")


def draw_title_block(ax, x0, y0, x1, y1):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, lw=THICK, edgecolor=INK, zorder=4))
    rows = [y1 - 0.42 - 0.2 * k for k in range(6)]  # top of each band below the title
    for y in rows[:-1]:
        line(ax, [(x0, y), (x1, y)], lw=0.5)
    ax.text(x0 + 0.08, y1 - 0.07, "BYU VERTICAL CLOUD LAB  ·  rePOWDER ATOMIZER CHARGE", fontsize=6.0,
            color=GREY, va="top")
    ax.text(x0 + 0.08, y1 - 0.19, "CHARGE CUP AND PLUG, Ø3/4 6063", fontsize=12, weight="bold", color=INK,
            va="top")

    def cell(xa, ya, key, val, fs=7.0):
        ax.text(xa + 0.06, ya - 0.03, key, fontsize=4.8, color=GREY, va="top")
        ax.text(xa + 0.06, ya - 0.10, val, fontsize=fs, color=INK, va="top")

    w = x1 - x0
    c1, c2, c3 = x0 + w * 0.42, x0 + w * 0.62, x0 + w * 0.80
    for c in (c1, c2, c3):
        line(ax, [(c, rows[0]), (c, rows[1])], lw=0.5)
    cell(x0, rows[0], "DWG NO.", "AC-CUP-PLUG")
    cell(c1, rows[0], "REV", "A")
    cell(c2, rows[0], "SHEET", "1 OF 1")
    cell(c3, rows[0], "PROJECTION", "")
    third_angle_symbol(ax, c3 + 0.27, rows[0] - 0.15, h=0.10)
    line(ax, [(c2, rows[1]), (c2, rows[2])], lw=0.5)
    cell(x0, rows[1], "SCALE", "CUP 1:1, PLUG 3:1, ON LETTER AT 100 %", fs=6.4)
    cell(c2, rows[1], "UNITS", "INCH [mm]", fs=6.4)
    cell(x0, rows[2], "MATERIAL  ·  FINISH",
         "6063-T52 ALUMINUM ROD, Ø3/4 (McMASTER 1640T16)  ·  AS MACHINED, DEGREASED", fs=6.0)
    cell(x0, rows[3], "UNLESS OTHERWISE SPECIFIED",
         ".XX ±.01   .XXX ±.005   ANGLES ±1°   BREAK SHARP EDGES .005-.015   DO NOT SCALE",
         fs=6.0)
    line(ax, [(c2, rows[5]), (c2, rows[4])], lw=0.5)
    cell(x0, rows[4], "DRAWN", "CLAUDE (AI) FOR R. GUYMON, 2026-10-19", fs=6.0)
    cell(c2, rows[4], "CHECKED", "", fs=6.0)
    ax.text(x0 + 0.06, (y0 + rows[5]) / 2, "HOW TO MAKE THEM: atomizer-charge/process-sheet/  ·  "
            "THIS SHEET'S SOURCE: atomizer-charge/drawing/cup_plug.py", fontsize=5.0, color=GREY, va="center")


def draw_revisions(ax, x0, y1, x1):
    h = 0.16
    ax.add_patch(Rectangle((x0, y1 - 2 * h), x1 - x0, 2 * h, fill=False, lw=0.7, edgecolor=INK, zorder=4))
    line(ax, [(x0, y1 - h), (x1, y1 - h)], lw=0.4)
    cols = [x0, x0 + 0.32, x1 - 0.75]
    for c in cols[1:]:
        line(ax, [(c, y1), (c, y1 - 2 * h)], lw=0.4)
    for c, k, v in zip(cols, ("REV", "DESCRIPTION", "DATE"),
                       ("A", "FIRST ISSUE: THE AS-MADE SIZES (#222, PR #277)", "2026-10-19")):
        ax.text(c + 0.05, y1 - h / 2, k, fontsize=5.4, color=GREY, va="center", weight="bold")
        ax.text(c + 0.05, y1 - 1.5 * h, v, fontsize=6.0, color=INK, va="center")


def main() -> None:
    fig = plt.figure(figsize=(11, 8.5))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 8.5)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((0.25, 0.25), 10.5, 8.0, fill=False, lw=1.4, edgecolor=INK))

    ax.text(0.45, 8.02, "Charge cup and plug, as made", fontsize=13, weight="bold", color=INK, va="center")
    ax.text(0.45, 7.80, "The sizes of the cups and plugs made for the first runs (#222), so new ones match them. "
            "Every part is drawn cut through the middle; hatching is metal.", fontsize=7.2, color=GREY, va="center")
    draw_revisions(ax, 7.35, 8.20, 10.70)

    draw_cup(ax)
    draw_plug(ax)
    draw_assembly(ax)
    y_end = draw_notes(ax, 6.55, 5.02)
    draw_variants(ax, 0.45, 1.80, 5.85)
    draw_title_block(ax, 6.45, 0.25, 10.75, 1.81)

    for ext in ("pdf", "png"):
        out = HERE / f"cup_plug.{ext}"
        fig.savefig(out, dpi=200 if ext == "png" else None)
        print("wrote", out.name)
    plt.close(fig)
    print(f"notes end at y = {y_end:.2f} in (title block top 1.81)")
    print(f"cup {cup_mass_g(BORE_D):.2f} g, plug {plug_mass_g(FIRST_PLUG_D, PLUG_L):.2f} g; "
          f"thin cup {cup_mass_g(THIN_BORE_D):.2f} g, thin plug {plug_mass_g(THIN_BORE_D, THIN_PLUG_L):.2f} g")


if __name__ == "__main__":
    main()

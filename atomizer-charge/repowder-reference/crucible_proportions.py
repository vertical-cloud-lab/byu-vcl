"""Crucible proportions scaled from Indutherm's section drawing (GU500 manual, Fig. 61).

None of the vendor documents (AMAZEMET's manual and facility guide, Indutherm's GU500
manual) dimension the crucible. Fig. 61 of the GU500 manual (the Indutherm furnace
inside the rePowder induction module) is a CAD section of the crucible chamber, so its
proportions can be measured and then scaled by one known length. These are estimates
to check the byu-vcl charge CAD against, not machining dimensions: measure the real
crucible before cutting anything.

The pixel spans below were read off the drawing as embedded in the PDF
(page 75, 819 x 583 px, square pixels). Edges were located by thresholding
rows and columns of the image.

Also prints the loading clearance past the sealing-rod adapter and its holder arm,
which sit over the crucible while it is filled, and whether a cylindrical slug fits
past the adapter.

Run with:  uv run --no-project --with matplotlib python crucible_proportions.py
Writes:    figures/crucible-proportions.png, next to this script
"""

from math import atan, degrees, pi
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Polygon, Rectangle, Wedge

# --- Pixel measurements from Fig. 61 (x across, y down) -----------------------
BORE_PX = 100  # inner wall to inner wall, x = 349..448
ROD_PX = 22  # sealing rod (C035), x = 388..409
GAP_PX = (BORE_PX - ROD_PX) / 2  # rod to wall, each side
WALL_PX = 16  # graphite wall (C008): 333..348 left, 449..466 right
RIM_Y = 305  # crucible rim = underside of the filling cone (C020)
CONE_TOP_Y = 272  # top face of the filling cone
FLOOR_START_Y = 447  # straight bore ends, conical floor begins
APEX_Y = 483  # floor cone extended to the axis (the pour hole starts here)
BOTTOM_Y = 507  # underside of the crucible
HOLE_PX = 12  # pour-hole channel below the apex, x = 393..404
TC_BOTTOM_Y = 390  # lower end of the wall thermocouple (C034)
ADAPTER_PX = 38  # sealing-rod adapter (C018) along the arm, x = 380..417
ADAPTER_BOTTOM_Y = 273  # lower end of the adapter, level with the top of the filling cone
ARM_UNDERSIDE_Y = 223  # underside of the holder arm (C017), rod closed

# --- Derived, in units of the bore diameter B ---------------------------------
B = BORE_PX
straight = (FLOOR_START_Y - RIM_Y) / B
floor = (APEX_Y - FLOOR_START_Y) / B
rim_to_apex = (APEX_Y - RIM_Y) / B
filling_cone = (RIM_Y - CONE_TOP_Y) / B
height = (BOTTOM_Y - RIM_Y) / B
rod, gap, wall, hole = ROD_PX / B, GAP_PX / B, WALL_PX / B, HOLE_PX / B
od = 1 + 2 * wall
floor_angle = degrees(atan(floor / 0.5))  # from horizontal

# Cavity volume (rim to apex) in B^3: cylinder + cone. The rod displaces the rest.
cavity_b3 = pi / 4 * straight + pi / 12 * floor
rod_b3 = pi / 4 * rod**2 * (rim_to_apex - rod / 2)


def scaled(bore_mm):
    """Every length in mm, plus the cavity volume in cm^3, for a given bore."""
    return {
        "Bore": bore_mm,
        "Sealing-rod Ø": rod * bore_mm,
        "Rod-to-wall gap": gap * bore_mm,
        "Graphite wall": wall * bore_mm,
        "Crucible OD": od * bore_mm,
        "Straight-wall depth": straight * bore_mm,
        "Rim to floor apex": rim_to_apex * bore_mm,
        "Filling-cone thickness": filling_cone * bore_mm,
        "Cone top to floor apex": (filling_cone + rim_to_apex) * bore_mm,
        "Cavity volume (cm³)": cavity_b3 * bore_mm**3 / 1000,
    }


# Three ways to fix the scale: Bartosz's 20 mm gap (9/17 call), AMAZEMET's quoted
# 225 cm^3, and Indutherm's 245 cm^3.
scales = {
    "gap = 20 mm": 20 / gap,
    "225 cm³\n(best fit)": (225_000 / cavity_b3) ** (1 / 3),
    "245 cm³": (245_000 / cavity_b3) ** (1 / 3),
}
table = {name: scaled(b) for name, b in scales.items()}


def loading(bore_mm):
    """Clearances in mm around the crucible mouth while it is filled, rod seated."""
    s = bore_mm / B
    return {
        "Adapter width": ADAPTER_PX * s,
        "Adapter bottom above rim": (RIM_Y - ADAPTER_BOTTOM_Y) * s,
        "Arm underside above cone top": (CONE_TOP_Y - ARM_UNDERSIDE_Y) * s,
        "Arm underside above rim": (RIM_Y - ARM_UNDERSIDE_Y) * s,
        "Band beside adapter": (BORE_PX - ADAPTER_PX) / 2 * s,
    }


def tipped_in_margin(bore_mm, slug_d, slug_len=63.5, step=0.5):
    """Worst-case room (mm) for a slug tipped in past the adapter, top leaning away from it.

    The slug's bottom rides against the rod. Above the adapter's lower end, its inner edge
    has to clear the adapter; at the rim, its outer edge has to stay inside the bore. The
    least tilt that clears the adapter is checked at every depth until the top is below the
    adapter. Negative means it doesn't fit.
    """
    s = bore_mm / B
    r_rod, r_bore, r_adapter = ROD_PX / 2 * s, BORE_PX / 2 * s, ADAPTER_PX / 2 * s
    h = (RIM_Y - ADAPTER_BOTTOM_Y) * s
    worst, depth = float("inf"), 0.0
    while depth <= slug_len - h:
        tilt = (r_adapter - r_rod) / (h + depth)  # tan of the least tilt
        outer = r_rod + slug_d * (1 + tilt**2) ** 0.5 + depth * tilt
        worst = min(worst, r_bore - outer)
        depth += step
    return worst

# --- Drawing -------------------------------------------------------------------
SURFACE, INK, INK2, ACCENT = "#fcfcfb", "#0b0b0b", "#52514e", "#2a78d6"
GRAPHITE, GRAPHITE_EDGE, CERAMIC, ROD = "#d9d8d4", "#8a8983", "#f1ede4", "#6d6c68"

plt.rcParams.update({"font.size": 10, "hatch.linewidth": 0.6})
fig = plt.figure(figsize=(11.5, 7.2), facecolor=SURFACE)
ax = fig.add_axes([0.02, 0.02, 0.50, 0.85], facecolor=SURFACE)
ax.set_aspect("equal")
ax.axis("off")

r_i, r_o = 0.5, 0.5 + wall
y_floor, y_apex, y_bot = -straight, -rim_to_apex, -height

# Graphite crucible: each half is one polygon (outer wall, bottom, hole, floor, bore).
for s in (-1, 1):
    half = [
        (s * r_i, 0),
        (s * r_o, 0),
        (s * r_o, y_bot),
        (s * hole / 2, y_bot),
        (s * hole / 2, y_apex),
        (s * r_i, y_floor),
    ]
    ax.add_patch(Polygon(half, closed=True, fc=GRAPHITE, ec=GRAPHITE_EDGE, lw=1.0, hatch="///"))

# Filling cone (top insulation, C020): conical mouth down to the bore.
mouth_top, mouth_y = 0.80, 0.10
for s in (-1, 1):
    ins = [
        (s * r_i, 0),
        (s * 1.05, 0),
        (s * 1.05, filling_cone),
        (s * mouth_top, filling_cone),
        (s * r_i, mouth_y),
    ]
    ax.add_patch(Polygon(ins, closed=True, fc=CERAMIC, ec=GRAPHITE_EDGE, lw=1.0, hatch=".."))

# Wall thermocouple (C034), right wall.
ax.plot([r_i + wall / 2] * 2, [filling_cone + 0.12, -(TC_BOTTOM_Y - RIM_Y) / B], color=INK, lw=2.2)

# Sealing rod (C035) with a rounded tip that sits in the pour hole.
tip_y = y_floor - (r_i - rod / 2) * floor / 0.5  # where the rod meets the floor cone
rod_top = filling_cone + 0.42
ax.add_patch(Rectangle((-rod / 2, tip_y), rod, rod_top - tip_y, fc=ROD, ec=INK, lw=0.8))
ax.add_patch(Wedge((0, tip_y), rod / 2, 180, 360, fc=ROD, ec=INK, lw=0.8))
ax.plot([0, 0], [y_bot - 0.12, rod_top + 0.08], color=INK2, lw=0.6, ls=(0, (8, 3, 2, 3)))


def dim_h(x0, x1, y, label=None, ext_from=None):
    """Horizontal dimension line with arrows; optional extension lines from ext_from."""
    ax.annotate("", (x0, y), (x1, y), arrowprops=dict(arrowstyle="<->", color=ACCENT, lw=1.1, shrinkA=0, shrinkB=0))
    if ext_from is not None:
        for x in (x0, x1):
            ax.plot([x, x], [ext_from, y], color=ACCENT, lw=0.6)
    if label:
        ax.text((x0 + x1) / 2, y + 0.04, label, ha="center", va="bottom", color=INK)


def dim_v(x, y0, y1, label, ext_from=None, rotate=True):
    ax.annotate("", (x, y0), (x, y1), arrowprops=dict(arrowstyle="<->", color=ACCENT, lw=1.1, shrinkA=0, shrinkB=0))
    if ext_from is not None:
        for y in (y0, y1):
            ax.plot([ext_from, x + 0.03], [y, y], color=ACCENT, lw=0.6)
    ax.text(x + 0.05, (y0 + y1) / 2, label, ha="left", va="center", color=INK, rotation=90 if rotate else 0)


dim_h(-r_i, r_i, -0.35)
ax.text(-0.31, -0.31, "bore\n1.00 B", ha="center", va="bottom", color=INK, linespacing=1.1)
dim_h(-r_i, -rod / 2, -0.95)
ax.text(-0.31, -0.91, f"gap\n{gap:.2f} B", ha="center", va="bottom", color=INK, linespacing=1.1)
y_rod_dim = rod_top - 0.06
dim_h(-rod / 2, rod / 2, y_rod_dim)
ax.plot([-rod / 2 - 0.22, -rod / 2], [y_rod_dim] * 2, color=ACCENT, lw=0.6)
ax.text(-rod / 2 - 0.25, y_rod_dim, f"rod Ø  {rod:.2f} B", ha="right", va="center", color=INK)
dim_h(-r_o, r_o, y_bot - 0.40, f"OD  {od:.2f} B", ext_from=y_bot - 0.02)
dim_h(-r_o, -r_i, -1.62)
ax.text(-r_o - 0.04, -1.62, f"wall {wall:.2f} B", ha="right", va="center", color=INK)

x1 = r_o + 0.20
dim_v(x1, 0, y_floor, f"straight wall  {straight:.2f} B", ext_from=r_o + 0.02)
dim_v(x1 + 0.34, 0, y_apex, f"rim → floor apex  {rim_to_apex:.2f} B", ext_from=r_o + 0.02)
dim_v(1.05 + 0.18, 0, filling_cone, f"{filling_cone:.2f} B", ext_from=1.07, rotate=False)

# Floor angle, at the left corner where there is room.
ax.add_patch(Arc((-r_i, y_floor), 0.56, 0.56, theta1=-floor_angle, theta2=0, color=ACCENT, lw=1.0))
ax.plot([-r_i, -r_i + 0.34], [y_floor, y_floor], color=ACCENT, lw=0.6)
ax.text(-r_i + 0.31, y_floor - 0.03, f"{floor_angle:.0f}°", ha="left", va="top", color=INK)

# Part labels (Indutherm consumable codes).
ax.text(-0.84, -1.22, "graphite\ncrucible\n(C008)", ha="center", va="center", color=INK2, fontsize=9)
ax.text(-0.78, filling_cone + 0.04, "filling cone /\ntop insulation\n(C020)", ha="center", va="bottom", color=INK2, fontsize=9)
ax.text(rod / 2 + 0.04, rod_top - 0.02, "sealing rod (C035)", ha="left", va="top", color=INK2, fontsize=9)
ax.text(r_i + wall / 2 + 0.04, filling_cone + 0.13, "wall thermocouple (C034)", ha="left", va="bottom", color=INK2, fontsize=9)
ax.text(hole / 2 + 0.03, y_bot - 0.05, "pour hole (nozzle seat)", ha="left", va="top", color=INK2, fontsize=9)

ax.set_xlim(-1.35, 1.75)
ax.set_ylim(-2.75, filling_cone + 0.55)

# --- Table ---------------------------------------------------------------------
tx = fig.add_axes([0.56, 0.22, 0.42, 0.62], facecolor=SURFACE)
tx.axis("off")
cols = list(table)
rows = list(table[cols[0]])
cell = [[r] + [f"{table[c][r]:.0f}" if "volume" in r else f"{table[c][r]:.1f}" for c in cols] for r in rows]
t = tx.table(cellText=cell, colLabels=["Lengths in mm"] + [f"scaled so\n{c}" for c in cols],
             colWidths=[0.34, 0.22, 0.22, 0.22], loc="upper center", cellLoc="center")
t.auto_set_font_size(False)
t.set_fontsize(9.5)
t.scale(1.0, 1.6)
for (r, c), k in t.get_celld().items():
    k.set_edgecolor("#d0cfca")
    k.set_facecolor(SURFACE)
    k.get_text().set_color(INK if r > 0 else INK2)
    if c == 0:
        k.get_text().set_ha("left")
        k.PAD = 0.04
    if r == 0:
        k.set_height(k.get_height() * 2.0)

fig.text(0.02, 0.965, "rePowder induction crucible: proportions scaled from Indutherm's section drawing",
         ha="left", va="top", fontsize=13, color=INK, weight="bold")
fig.text(0.02, 0.925, "GU500 manual Fig. 61 is undimensioned, so everything is a ratio to the bore B. "
         "Estimates only: measure the real crucible before machining.", ha="left", va="top", fontsize=9.5, color=INK2)
fig.text(0.56, 0.2, "225 cm³ is AMAZEMET's quoted size and 245 cm³ the GU500 data sheet.\n"
         "Scaled to 225 cm³, the drawing matches all three numbers from the 9/17\n"
         "call: about 20 mm rod-to-wall, 10–11 cm inner height, and about 12 cm to\n"
         "the top of the insulation. byu-vcl's charge CAD assumes a Ø52 bore (a\n"
         f"flat-floored 225 cm³) and a Ø12 rod. The rod takes ≈{100 * rod_b3 / cavity_b3:.0f}% of the cavity.",
         ha="left", va="top", fontsize=9, color=INK2, linespacing=1.4)

out = Path(__file__).parent / "figures" / "crucible-proportions.png"
fig.savefig(out, dpi=130, facecolor=SURFACE)

if __name__ == "__main__":
    print(f"floor angle {floor_angle:.1f} deg from horizontal; cavity {cavity_b3:.3f} B^3")
    for name, vals in table.items():
        print(name, {k: round(v, 1) for k, v in vals.items()})
    print("\nLoading clearance (mm), and room for slugs past the adapter (negative = doesn't fit):")
    for name, b in scales.items():
        name = name.replace("\n", " ")
        print(name, {k: round(v, 1) for k, v in loading(b).items()})
        band = loading(b)["Band beside adapter"]
        for label, d in {'3/4"': 19.05, '5/8"': 15.875, '1/2"': 12.7}.items():
            print(f"   {label} slug: straight down {band - d:+.1f}, tipped in {tipped_in_margin(b, d):+.1f}")
    print("wrote", out)

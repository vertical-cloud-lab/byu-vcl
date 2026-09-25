"""Dimensioned shop drawing of the parts the prototyping lab makes (issue #222).

One US-Letter landscape sheet.  The sections are drawn from the same (r, z)
profiles that ``charge_cad.py`` revolves into the STEP files, so the drawing and
the models cannot disagree.  Parts are 1:1 when printed at 100 %, plugs 3:1.

Usage:  python drawings.py      (writes drawings/charge_parts.pdf and .png)
"""

from __future__ import annotations

import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle

import charge_cad as cad

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "drawings"

INK = "#0b0b0b"
INK2 = "#52514e"
HATCH = "#8a8f96"
FS = 7.0  # dimension text, pt
plt.rcParams["hatch.linewidth"] = 0.35
plt.rcParams["hatch.color"] = HATCH

MM = 1 / 25.4  # page inches per mm at 1:1


def fmt(mm: float, places: int = 3) -> str:
    inch = f"{mm / 25.4:.{places}f}".lstrip("0")
    return f"{inch} [{mm:.2f}]"


def full_outline(profile):
    """Mirror a half-profile that starts and ends on the axis into one closed outline."""
    return profile + [(-r, z) for r, z in reversed(profile[1:-1])]


class View:
    """A section view placed on the page; x = radius, y = height (mm)."""

    def __init__(self, ax, x0, y0, scale=1.0):
        self.ax, self.x0, self.y0, self.s = ax, x0, y0, scale

    def p(self, r, z):
        return self.x0 + r * MM * self.s, self.y0 + z * MM * self.s

    def section(self, profile, hatch="////"):
        on_axis = profile[0][0] == 0 and profile[-1][0] == 0
        outlines = [full_outline(profile)] if on_axis else [profile, [(-r, z) for r, z in profile]]
        for outline in outlines:
            pts = [self.p(r, z) for r, z in outline]
            self.ax.add_patch(Polygon(pts, closed=True, fill=False, hatch=hatch, lw=0, edgecolor=HATCH))
            self.ax.add_patch(Polygon(pts, closed=True, fill=False, lw=0.8, edgecolor=INK))

    def centreline(self, z0, z1):
        (x, y0), (_, y1) = self.p(0, z0), self.p(0, z1)
        self.ax.plot([x, x], [y0 - 0.08, y1 + 0.08], color=INK2, lw=0.45, ls=(0, (8, 2, 1.5, 2)))

    def hdim(self, r1, r2, z_ext, gap_in, text):
        """Horizontal dimension between radii r1, r2 (mm), gap_in page-inches above (+) or below (-) z_ext."""
        (x1, ye), (x2, _) = self.p(r1, z_ext), self.p(r2, z_ext)
        yd = ye + gap_in
        up = 1 if gap_in > 0 else -1
        for x in (x1, x2):
            self.ax.plot([x, x], [ye + up * 0.03, yd + up * 0.05], color=INK2, lw=0.4)
        arrow(self.ax, (x1, yd), (x2, yd))
        self.ax.text((x1 + x2) / 2, yd + up * 0.035, text, ha="center", va="bottom" if up > 0 else "top",
                     fontsize=FS, color=INK)
        return yd

    def vdim(self, z1, z2, r_ext, gap_in, text):
        """Vertical dimension between heights z1, z2 (mm), gap_in page-inches right (+) or left (-) of r_ext."""
        (xe, y1), (_, y2) = self.p(r_ext, z1), self.p(r_ext, z2)
        xd = xe + gap_in
        out = 1 if gap_in > 0 else -1
        for y in (y1, y2):
            self.ax.plot([xe + out * 0.03, xd + out * 0.05], [y, y], color=INK2, lw=0.4)
        arrow(self.ax, (xd, y1), (xd, y2))
        self.ax.text(xd + out * 0.05, (y1 + y2) / 2, text, ha="left" if out > 0 else "right", va="center",
                     fontsize=FS, color=INK, linespacing=1.2)

    def title(self, y, text, subs):
        x, _ = self.p(0, 0)
        self.ax.text(x, y, text, ha="center", va="bottom", fontsize=8.6, weight="bold", color=INK)
        for i, s in enumerate(subs):
            self.ax.text(x, y - 0.035 - i * 0.125, s, ha="center", va="top", fontsize=6.5, color=INK2)


def plug_view(ax, v, profile, r, length, vent_d):
    """Plug section with the through-hole called out as what it is: an air escape."""
    v.section(profile)
    rv = vent_d / 2
    (x0, y0), (x1, y1) = v.p(0, -0.6), v.p(0, length + 0.6)
    ax.plot([x0, x1], [y0, y1], color="#2a78d6", lw=0.9)
    ax.annotate("", xy=(x1, y1 + 0.10), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color="#2a78d6", lw=0.9, mutation_scale=6))
    ax.text(x1 + 0.06, y1 + 0.13, "air out", fontsize=FS, color="#2a78d6", ha="left", va="center")
    (xl, yl), (xr, _) = v.p(-rv, length / 2), v.p(rv, length / 2)
    ax.annotate("\u00d81 mm hole,\nright through", xy=((xl + xr) / 2, yl), xytext=(xr + 0.55, yl),
                fontsize=FS, color=INK, ha="left", va="center", linespacing=1.2,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.45, shrinkA=2, shrinkB=2))
    (xa, ya) = v.p(-r, 0.25)
    ax.annotate("taper, so it\nstarts square", xy=(xa, ya), xytext=(xa - 0.28, ya - 0.1),
                fontsize=FS, color=INK, ha="right", va="center", linespacing=1.2,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.45, shrinkA=2, shrinkB=2))
    return v


def arrow(ax, a, b):
    ax.annotate("", xy=b, xytext=a,
                arrowprops=dict(arrowstyle="<|-|>", lw=0.5, color=INK, mutation_scale=5, shrinkA=0, shrinkB=0))


def main() -> None:
    OUT.mkdir(exist_ok=True)
    fig = plt.figure(figsize=(11, 8.5))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 8.5)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((0.25, 0.25), 10.5, 8.0, fill=False, lw=0.9, edgecolor=INK))

    R, L = cad.STOCK_D / 2, cad.SLUG_L
    rb, depth = cad.CUP_BORE_D / 2, cad.CUP_BORE_DEPTH
    trb, TL, tf = cad.THIN_BORE_D / 2, cad.THIN_L, cad.THIN_FLOOR
    ro, rs = cad.SLEEVE_OD / 2, cad.SLEEVE_BORE_D / 2
    ROW1, ROW2, ROW_LID = 4.25, 1.72, 1.95
    T1, T2 = 7.62, 3.85  # title baselines

    # --- Row 1: the 2.5 in parts, 1:1 --------------------------------------
    v = View(ax, 1.15, ROW1)
    v.section(cad.solid_slug_profile())
    v.centreline(0, L)
    v.hdim(-R, R, L, 0.2, "\u00d8" + fmt(cad.STOCK_D))
    v.vdim(0, L, R, 0.3, fmt(L))
    v.title(T1, "P1  Solid slug", ["6063-T52 \u00b7 qty 2 (E2)", "OD as received \u00b7 .02 \u00d7 45\u00b0 both ends"])

    v = View(ax, 4.15, ROW1)
    v.section(cad.std_cup_profile())
    v.centreline(0, L)
    v.hdim(-R, R, L, 0.2, "\u00d8" + fmt(cad.STOCK_D))
    v.hdim(-rb, rb, L, 0.48, "\u00d8" + fmt(cad.CUP_BORE_D) + " reamed")
    v.vdim(0, L, R, 0.3, fmt(L))
    v.vdim(L - depth, L, -R, -0.3, fmt(depth) + "\ndeep")
    v.title(T1, "P2  Cup", ["6063-T52 \u00b7 qty 10 (E1, E3\u2013E6)", "drill then ream \u00b7 118\u00b0 bottom is fine"])

    v = View(ax, 7.5, ROW1)
    v.section(cad.sleeve_profile(), hatch="\\\\")
    v.centreline(0, cad.SLEEVE_L)
    v.hdim(-ro, ro, cad.SLEEVE_L, 0.2, "\u00d8" + fmt(cad.SLEEVE_OD))
    v.hdim(-rs, rs, cad.SLEEVE_L, 0.48, "\u00d8 = measured P2 OD + .001\u2013.002 (slip fit)")
    v.vdim(0, cad.SLEEVE_L, ro, 0.3, fmt(cad.SLEEVE_L) + "\n= P2 length")
    v.title(T1, "F1  Press sleeve", ["mild steel \u00b7 qty 1 \u00b7 only for E4",
                                     "stops the cup wall bulging under the press"])

    # --- Row 2: the lids, 3:1, and the small cup ---------------------------
    v = View(ax, 1.75, ROW2)
    v.section(cad.thin_cup_profile())
    v.centreline(0, TL)
    v.hdim(-R, R, TL, 0.2, "\u00d8" + fmt(cad.STOCK_D))
    v.hdim(-trb, trb, TL, 0.48, "\u00d8" + fmt(cad.THIN_BORE_D) + " flat bottom")
    v.vdim(0, TL, R, 0.3, fmt(TL))
    v.vdim(tf, TL, -R, -0.3, fmt(TL - tf))
    v.title(T2, "P4  Small cup", ["6063-T52 \u00b7 qty 2 (E7, later)", "1/16\" wall \u00b7 " + fmt(tf) + " floor"])

    v = View(ax, 4.55, ROW_LID, scale=3.0)
    plug_view(ax, v, cad.plug_profile(), rb, cad.PLUG_L, cad.VENT_D)
    v.hdim(-rb, rb, cad.PLUG_L, 0.34, "\u00d8 = that cup's measured hole + .0005\u2013.001")
    v.vdim(0, cad.PLUG_L, rb, 0.62, fmt(cad.PLUG_L))
    v.title(T2, "P3  Lid for P2   (3:1)", ["6063-T52 \u00b7 qty 10 \u00b7 one per cup, not interchangeable"])

    v = View(ax, 8.35, ROW_LID, scale=3.0)
    plug_view(ax, v, cad.plug_profile(cad.THIN_BORE_D, cad.THIN_PLUG_L), trb, cad.THIN_PLUG_L, cad.VENT_D)
    v.hdim(-trb, trb, cad.THIN_PLUG_L, 0.34, "\u00d8 = measured hole + .0005")
    v.vdim(0, cad.THIN_PLUG_L, trb, 0.62, fmt(cad.THIN_PLUG_L, 4))
    v.title(T2, "P5  Lid for P4   (3:1)", ["6063-T52 \u00b7 qty 2 \u00b7 same hole and taper as P3"])

    notes_l = [
        "NOTES",
        "1  All parts from the 3/4\" 6063-T52 bar on hand (McMaster 1640T16). Inches [mm].",
        "2  Break the outside edges .02 [0.5] \u00d7 45\u00b0 and deburr the holes. No marker, no stamping.",
        "3  Make a cup, measure its hole, then turn that cup's lid .0005\u2013.001\" bigger, so it",
        "    presses in. No more than .001\": the 1/8\" wall splits at about twice that.",
        "    Bag each lid with the cup it was made for - they are not interchangeable.",
    ]
    notes_r = [
        "",
        "4  Every lid gets the \u00d81 mm hole. The chamber is pumped down before melting, and air",
        "    shut under a solid lid has to escape through the powder instead (see #104).",
        "5  E4 only: stand the filled cup inside F1 and press the lid flush. F1 is the same length",
        "    as the cup, so the press bottoms out at flush. Push the cup out with a 5/8\" drift.",
        "6  Degrease in IPA, dry, weigh each part to 0.01 g, then bag and label it.",
        "Parts 1:1 on Letter at 100 %, lids 3:1 \u00b7 STEP files: atomizer-charge/cad/step/",
    ]
    ax.add_patch(Rectangle((0.45, 0.45), 10.1, 0.95, fill=False, lw=0.6, edgecolor=INK2))
    for col, lines in ((0.56, notes_l), (5.55, notes_r)):
        for i, line in enumerate(lines):
            last = col > 1 and i == len(lines) - 1
            ax.text(col, 1.31 - i * 0.111, line, fontsize=6.3, weight="bold" if line == "NOTES" else "normal",
                    color=INK2 if last else INK, va="center")

    ax.text(0.45, 8.08, "rePowder first runs: parts for the prototyping lab", fontsize=12.5, weight="bold",
            color=INK, va="center")
    ax.text(0.45, 7.87, "Every part is shown cut through the middle; hatching is metal. The cup has to fit the crucible \u2013 "
            "confirm that before cutting \u00b7 issue #222", fontsize=7.0, color=INK2, va="center")

    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"charge_parts.{ext}", dpi=200 if ext == "png" else None)
        print("wrote", (OUT / f"charge_parts.{ext}").relative_to(HERE))
    plt.close(fig)


if __name__ == "__main__":
    main()

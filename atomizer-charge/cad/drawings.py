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
    ROW1, ROW2 = 4.3, 1.7
    T1, T2 = 7.66, 3.9  # title baselines

    # --- Row 1: 2.5" parts, 1:1 --------------------------------------------
    v = View(ax, 1.2, ROW1)
    v.section(cad.solid_slug_profile())
    v.centreline(0, L)
    v.hdim(-R, R, L, 0.2, "Ø" + fmt(cad.STOCK_D))
    v.vdim(0, L, R, 0.3, fmt(L))
    v.title(T1, "P1  Solid slug", ["6063-T52 · qty 2 (E2)", "OD as received · .02 × 45° both ends"])

    v = View(ax, 4.2, ROW1)
    v.section(cad.std_cup_profile())
    v.centreline(0, L)
    v.hdim(-R, R, L, 0.2, "Ø" + fmt(cad.STOCK_D))
    v.hdim(-rb, rb, L, 0.45, "Ø" + fmt(cad.CUP_BORE_D) + " ream")
    v.vdim(0, L, R, 0.3, fmt(L))
    v.vdim(L - depth, L, -R, -0.3, fmt(depth) + "\nto full Ø")
    v.title(T1, "P2  Standard cup", ["6063-T52 · qty 10 (E1, E3–E6)", "118° drill point OK · rim .012 × 45°"])

    v = View(ax, 7.3, ROW1)
    v.section(cad.sleeve_profile(), hatch="\\\\\\\\")
    v.centreline(0, cad.SLEEVE_L)
    v.hdim(-ro, ro, cad.SLEEVE_L, 0.2, "Ø" + fmt(cad.SLEEVE_OD))
    v.hdim(-rs, rs, cad.SLEEVE_L, 0.45, "Ø = measured P2 OD + .001–.002 (slip)")
    v.vdim(0, cad.SLEEVE_L, ro, 0.3, fmt(cad.SLEEVE_L) + "\n= P2 length")
    v.title(T1, "F1  Press support sleeve", ["mild steel (1018, 12L14) · qty 1 · E4 only", ".02 × 45° both ends, bore lead-ins"])

    # --- Row 2: short parts at 1:1, plugs at 3:1 -----------------------------
    v = View(ax, 1.9, ROW2)
    v.section(cad.thin_cup_profile())
    v.centreline(0, TL)
    v.hdim(-R, R, TL, 0.2, "Ø" + fmt(cad.STOCK_D))
    v.hdim(-trb, trb, TL, 0.45, "Ø" + fmt(cad.THIN_BORE_D) + " flat bottom")
    v.vdim(0, TL, R, 0.3, fmt(TL))
    v.vdim(tf, TL, -R, -0.3, fmt(TL - tf))
    v.title(T2, "P4  Thin-wall cup", ["6063-T52 · qty 2 (E7, later)", "1/16\" wall · " + fmt(tf) + " floor"])

    v = View(ax, 4.75, ROW2, scale=3.0)
    v.section(cad.plug_profile())
    v.centreline(0, cad.PLUG_L)
    v.hdim(-rb, rb, cad.PLUG_L, 0.2, "Ø = measured P2 bore + .0005–.001")
    v.vdim(0, cad.PLUG_L, rb, 0.25, fmt(cad.PLUG_L))
    v.title(T2, "P3  Plug for P2   (3:1)", ["6063-T52 · qty 10 · one per cup", "Ø1 mm [.040, #60] vent THRU · 15° lead-in .06 long"])

    v = View(ax, 8.05, ROW2, scale=3.0)
    v.section(cad.plug_profile(cad.THIN_BORE_D, cad.THIN_PLUG_L))
    v.centreline(0, cad.THIN_PLUG_L)
    v.hdim(-trb, trb, cad.THIN_PLUG_L, 0.2, "Ø = measured P4 bore + .0005")
    v.vdim(0, cad.THIN_PLUG_L, trb, 0.25, fmt(cad.THIN_PLUG_L, 4))
    v.title(T2, "P5  Plug for P4   (3:1)", ["6063-T52 · qty 2", "Ø1 mm vent THRU · same lead-in as P3"])

    notes_l = [
        "NOTES",
        "1  P1–P5 from the 3/4\" 6063-T52 bar on hand (McMaster 1640T16). Inches [mm].",
        "2  Outer edges .02 [0.5] × 45°, deburr bores. No marker ink, scribing or stamping.",
        "3  Make each cup first, MEASURE its bore, then turn that cup's plug to +.0005–.001\"",
        "    over it. Never more than .001\": P2's 1/8\" wall is at ~100 MPa hoop stress there",
        "    (6063-T52 yield ≥ 110 MPa). Bag each cup with its own plug.",
        "4  Every plug is vented: gas sealed in with powder can eject melt (#104, #134),",
        "    and the chamber is pumped down before melting.",
    ]
    notes_r = [
        "",
        "5  Slug OD ≤ measured rod-to-wall gap − 0.7 mm (Al grows ~1.4 % by 600 °C, graphite",
        "    ~0.3 %). A max-tolerance bar (Ø.764) needs a 20.1 mm gap; otherwise skim the ODs.",
        "6  After machining: degrease in IPA, dry, weigh each part to 0.01 g, bag, label the bag.",
        "7  F1 (E4 only): stand the filled cup in F1 on a flat plate, press the plug flush. F1 is",
        "    the cup's length, so the platen bottoms out at flush. Push out with a Ø5/8\" drift.",
        "8  Crucible geometry is inferred, not measured: check Ø52 bore / Ø12 rod before cutting.",
        "Parts 1:1 printed on Letter at 100 %, plugs 3:1 · STEP: atomizer-charge/cad/step/",
    ]
    ax.add_patch(Rectangle((0.45, 0.45), 10.1, 0.95, fill=False, lw=0.6, edgecolor=INK2))
    for col, lines in ((0.56, notes_l), (5.55, notes_r)):
        for i, line in enumerate(lines):
            last = col > 1 and i == len(lines) - 1
            ax.text(col, 1.31 - i * 0.111, line, fontsize=6.3, weight="bold" if line == "NOTES" else "normal",
                    color=INK2 if last else INK, va="center")

    ax.text(0.45, 8.08, "rePowder first-run charges: parts for the prototyping lab", fontsize=12.5, weight="bold",
            color=INK, va="center")
    ax.text(0.45, 7.87, "Sections through the axis, hatched = material. Drawn from the same profiles as the STEP "
            "files · issue #222 · 2026-09-24", fontsize=7.0, color=INK2, va="center")

    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"charge_parts.{ext}", dpi=200 if ext == "png" else None)
        print("wrote", (OUT / f"charge_parts.{ext}").relative_to(HERE))
    plt.close(fig)


if __name__ == "__main__":
    main()

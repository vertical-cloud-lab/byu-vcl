"""Draw the candidate electrodes to scale, for designing a holder.

Reads docs/electrode-dimensions.csv and writes docs/electrode-dimensions.png.
Left: side views, active end down, every electrode on the same millimetre scale.
Right: top view of the three 1/4 in (6.35 mm) CH Instruments bodies in a
triangle, the smallest opening they pass through, and a 20 mL vial for scale.

Diameters a vendor does not publish (od_published = no) are drawn dashed at
ASSUMED_OD_MM and labelled as such: measure the part before designing to them.

    python scripts/plot_electrode_dimensions.py
"""

import csv
import math
from collections import OrderedDict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "docs" / "electrode-dimensions.csv"
PNG_PATH = ROOT / "docs" / "electrode-dimensions.png"

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"

# Materials, not series: each part is labelled, so colour only helps the eye.
FILL = {
    "polymer": "#d9d8d2",
    "glass": "#dcebf9",
    "brass": "#eda100",
    "platinum": "#52514e",
    "graphite": "#3b3b39",
}
EDGE = {"glass": "#2a78d6"}

DRAW = ["chi104", "chi111", "chi115", "atlas_ref", "edaq_et072", "graphite_10"]
ASSUMED_OD_MM = 12.0  # drawing width only, for the Atlas reference
LIQUID_MM = 25.0  # suggested liquid surface above the disc face
GAP_MM = 24.0  # space between electrodes in the side view
SHORT = {
    "chi104": ("CHI104", "working", "Ø 6.35 body"),
    "chi111": ("CHI111", "reference", "Ø 4.0 glass\nØ 5.8–6.35 cap"),
    "chi115": ("CHI115", "counter", "Ø 0.5 wire\nØ 6.35 body"),
    "atlas_ref": ("Atlas", "reference", "Ø not published"),
    "edaq_et072": ("eDAQ ET072", "leakless ref.", "Ø 2.0"),
    "graphite_10": ("Graphite rod", "counter", "Ø 10.0"),
}

# Top view: three 1/4 in bodies at 120 degrees.
BODY_OD = 6.35
PITCH = 9.0  # centre-to-centre
HOLE = 6.6  # printed bore before fit-testing
VIAL_OD = 28.0


def load():
    parts = OrderedDict()
    with CSV_PATH.open(newline="") as f:
        for r in csv.DictReader(f):
            parts.setdefault(r["key"], []).append(r)
    for segs in parts.values():
        segs.sort(key=lambda r: int(r["seg"]))
    return parts


def side_view(ax, parts):
    x = 0.0
    for key in DRAW:
        segs = parts[key]
        widths = [float(s["od_mm"]) if s["od_mm"] else ASSUMED_OD_MM for s in segs]
        half = max(widths) / 2
        cx = x + half
        y = 0.0
        for s, w in zip(segs, widths):
            h = float(s["length_mm"])
            mat = s["material"]
            dashed = s["od_published"] == "no"
            ax.add_patch(
                Rectangle(
                    (cx - w / 2, y),
                    w,
                    h,
                    facecolor="none" if dashed else FILL[mat],
                    edgecolor=EDGE.get(mat, INK) if not dashed else INK_2,
                    linewidth=0.9,
                    linestyle=(0, (3, 2)) if dashed else "-",
                )
            )
            # Segment length, right of the part.
            ax.annotate(
                f"{h:g}",
                (cx + w / 2 + 0.8, y + h / 2),
                fontsize=7,
                color=INK_2,
                va="center",
            )
            y += h
        if key == "chi104":  # the disc in the end face
            ax.add_patch(Rectangle((cx - 1.5, -0.6), 3.0, 1.2, color=INK))
        name, role, ods = SHORT[key]
        ax.text(cx, -5, name, ha="center", va="top", fontsize=8, color=INK, weight="bold")
        ax.text(cx, -11, f"{role}\n{y:g} mm long\n{ods}", ha="center", va="top", fontsize=7, color=INK_2, linespacing=1.4)
        x += 2 * half + GAP_MM
    ax.axhspan(0, LIQUID_MM, color="#dcebf9", alpha=0.35, zorder=0, linewidth=0)
    ax.text(x - GAP_MM + 9, LIQUID_MM / 2, f"0–{LIQUID_MM:g} mm:\nsuggested\nliquid level", fontsize=7, color=INK_2, va="center")
    ax.axhline(0, color=MUTED, linewidth=0.6, zorder=0)
    ax.set_xlim(-4, x + 8)
    ax.set_ylim(-34, 160)
    ax.set_aspect("equal")
    ax.set_yticks(range(0, 161, 20))
    ax.set_ylabel("mm above the active end", color=INK_2, fontsize=8)
    ax.tick_params(axis="y", colors=INK_2, labelsize=7)
    ax.set_xticks([])
    ax.grid(axis="y", color=GRID, linewidth=0.5)
    for side in ("top", "right", "bottom"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["left"].set_bounds(0, 160)
    ax.set_title(
        "Side views to scale, active end down. Dashed: diameter not published (drawn 12 mm), measure it",
        fontsize=9,
        color=INK,
        loc="left",
    )


def top_view(ax):
    r = PITCH / math.sqrt(3)  # pitch-circle radius
    names = ["WE CHI104", "RE CHI111", "CE CHI115"]
    for i, name in enumerate(names):
        a = math.radians(90 + 120 * i)
        cx, cy = r * math.cos(a), r * math.sin(a)
        ax.add_patch(Circle((cx, cy), HOLE / 2, facecolor=SURFACE, edgecolor=MUTED, linewidth=0.8, linestyle=(0, (2, 2))))
        ax.add_patch(Circle((cx, cy), BODY_OD / 2, facecolor=FILL["polymer"], edgecolor=INK, linewidth=0.9))
        ax.text(cx, cy, name.replace(" ", "\n"), ha="center", va="center", fontsize=7, color=INK, linespacing=1.2)
    env = r + BODY_OD / 2
    ax.add_patch(Circle((0, 0), env, fill=False, edgecolor=INK, linewidth=0.9))
    ax.add_patch(Circle((0, 0), VIAL_OD / 2, fill=False, edgecolor=MUTED, linewidth=0.8, linestyle=(0, (4, 3))))
    ax.text(0, -env - 0.8, f"bodies pass a {2 * env:.1f} mm opening", ha="center", va="top", fontsize=7, color=INK)
    ax.text(0, -VIAL_OD / 2 - 1.0, "20 mL vial, 28 mm OD (neck ID: measure)", ha="center", va="top", fontsize=7, color=INK_2)
    ax.set_xlim(-17, 17)
    ax.set_ylim(-19.5, 17)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(
        f"Top view of the CHI set: 6.35 mm bodies\n{PITCH:g} mm apart; dashed: {HOLE:g} mm printed bore",
        fontsize=9,
        color=INK,
        loc="left",
    )


def main():
    parts = load()
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(12, 7.2), dpi=150, gridspec_kw={"width_ratios": [2.15, 1]}
    )
    fig.patch.set_facecolor(SURFACE)
    for ax in (ax1, ax2):
        ax.set_facecolor(SURFACE)
    side_view(ax1, parts)
    top_view(ax2)
    fig.text(
        0.01,
        0.01,
        "Sources: CH Instruments drawings (CHI101-104, CHI111, CHI115), Atlas Scientific spec sheet, "
        "eDAQ ET072 datasheet, ChemicalStore GR4BAR10X100. All in docs/electrode-dimensions.csv.",
        fontsize=6.5,
        color=MUTED,
    )
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(PNG_PATH, facecolor=SURFACE)
    print(f"wrote {PNG_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

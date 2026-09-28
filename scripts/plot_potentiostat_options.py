"""Plot potentiostat options as price vs. maximum current.

Reads docs/potentiostat-options.csv and writes docs/potentiostat-price-vs-current.png.
Each option is placed at its representative price; where the thread found a spread
of prices (several listings, or new vs. refurbished) a line spans the range. Filled
markers have EIS built in or as an internal option; hollow ones do not. Rows with
plot=no (quote-only, sold out, or no live listing found) are left to the table.

    python scripts/plot_potentiostat_options.py
"""

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "docs" / "potentiostat-options.csv"
PNG_PATH = ROOT / "docs" / "potentiostat-price-vs-current.png"

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"

# Three routes, three categorical slots, each with its own marker shape.
ROUTES = {
    "build": ("Build", "#2a78d6", "o"),
    "used": ("Buy used", "#eb6834", "s"),
    "new": ("Buy new or refurbished", "#1baf7a", "^"),
}

BASELINE_MA = 10  # Rodeostat HC, the instrument we are trying to beat


def money(x, _pos):
    return f"${x / 1000:g}k" if x >= 1000 else f"${x:g}"


def current(y, _pos):
    return f"{y / 1000:g} A" if y >= 1000 else f"{y:g} mA"


def main():
    with CSV_PATH.open(newline="") as f:
        rows = [r for r in csv.DictReader(f) if r["plot"] == "yes"]

    fig, ax = plt.subplots(figsize=(10, 6.4), dpi=150)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    for r in rows:
        name, color, marker = ROUTES[r["route"]]
        x = float(r["price_usd"])
        lo, hi = float(r["price_usd_low"]), float(r["price_usd_high"])
        y = float(r["max_current_mA"])
        if hi > lo:
            ax.plot([lo, hi], [y, y], color=color, lw=2, solid_capstyle="round", zorder=2)
        eis = r["eis"] in ("yes", "option")
        ax.scatter(
            x, y, s=90, marker=marker, zorder=3,
            facecolor=color if eis else SURFACE, edgecolor=color, linewidth=2,
        )
        ax.annotate(
            r["label"].replace("\\n", "\n"), (x, y),
            xytext=(float(r["label_dx"]), float(r["label_dy"])), textcoords="offset points",
            ha=r["label_ha"], va="center", fontsize=8.5, color=INK_2, zorder=4,
        )

    ax.axhline(BASELINE_MA, color=MUTED, lw=1, ls=(0, (4, 3)), zorder=1)
    ax.annotate(
        "Rodeostat HC limit (±10 mA)", (1, BASELINE_MA), xycoords=("axes fraction", "data"),
        xytext=(-4, 4), textcoords="offset points", ha="right", va="bottom",
        fontsize=8.5, color=MUTED,
    )

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(150, 20000)
    ax.set_ylim(1, 5000)
    ax.set_xticks([200, 500, 1000, 2000, 5000, 10000, 20000])
    ax.xaxis.set_major_formatter(FuncFormatter(money))
    ax.xaxis.set_minor_formatter(FuncFormatter(lambda *_: ""))
    ax.yaxis.set_major_formatter(FuncFormatter(current))
    ax.set_xlabel("Price, USD (log scale)", color=INK_2)
    ax.set_ylabel("Maximum current (log scale)", color=INK_2)
    ax.tick_params(colors=INK_2, which="both")
    ax.grid(True, which="major", color=GRID, lw=0.8)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(AXIS)

    handles = [
        Line2D([], [], marker=m, ls="", markersize=9, markerfacecolor=c, markeredgecolor=c, label=n)
        for n, c, m in ROUTES.values()
    ]
    handles += [
        Line2D([], [], marker="o", ls="", markersize=9, markerfacecolor=INK_2,
               markeredgecolor=INK_2, label="Filled: EIS built in or an internal option"),
        Line2D([], [], marker="o", ls="", markersize=9, markerfacecolor=SURFACE,
               markeredgecolor=INK_2, markeredgewidth=2, label="Hollow: no EIS"),
        Line2D([], [], color=INK_2, lw=2, label="Line: range of prices seen"),
    ]
    ax.legend(handles=handles, loc="lower right", frameon=False, fontsize=8.5, labelcolor=INK_2)

    ax.set_title(
        "Potentiostat options: price vs. maximum current",
        loc="left", fontsize=13, color=INK, pad=36,
    )
    ax.text(
        0, 1.015, "Asking prices checked Sept 2026 (Squidstat Plus: Admiral's early-2026 quotes). Quote-only options\n"
        "(EmStat4S HR, Autolab, Ivium) and used models with no live listing (VersaSTAT, CHI) are left to the table.",
        transform=ax.transAxes, fontsize=8.5, color=INK_2, va="bottom",
    )
    fig.tight_layout()
    fig.savefig(PNG_PATH, facecolor=SURFACE)
    print(f"wrote {PNG_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

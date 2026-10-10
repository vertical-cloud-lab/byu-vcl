"""Labour-vs-BOM cost analysis for the ten contributed projects (Table 1).

Derives the quantitative backbone of the revised Perspective: the *break-even
wage* at which build labour costs as much as the bill of materials, the labour
share of true first-build cost, and the sensitivity of both to the assumed
loaded hourly rate.

Inputs are the self-reported cost-to-reproduce and time-to-reproduce figures
already published in Table 1 of the v1 manuscript (10.26434/chemrxiv-2025-zhkrf).
No new data is introduced here.

Outputs (written next to this script):
  table1-derived.csv     per-project derived quantities
  sensitivity.csv        labour share as a function of loaded rate
  ../figures/fig1-labour-vs-bom.png

Run:  python labor_cost_analysis.py
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parent
FIGDIR = HERE.parent / "figures"

# Validated categorical slots 1 and 2 from the project palette.
# Checked with the dataviz validator (light surface): CVD dE 24.7, normal dE 33.6,
# both >= 3:1 contrast on white. Do not substitute by eye.
C_BOM = "#2a78d6"  # blue
C_LABOUR = "#eb6834"  # orange
SURFACE = "#ffffff"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#d8d7d2"

# Rates spanning plausible fully loaded costs for the people who actually do
# these builds, from a graduate researcher to a professional automation engineer.
RATES = (25.0, 50.0, 75.0)
BAND = (25.0, 75.0)


@dataclass(frozen=True)
class Project:
    name: str
    short: str
    bom_low: float
    bom_high: float
    hours: float
    note: str = ""

    @property
    def bom(self) -> float:
        """Midpoint of the reported BOM range."""
        return (self.bom_low + self.bom_high) / 2

    @property
    def breakeven_wage(self) -> float:
        """Loaded hourly rate at which labour cost equals the BOM."""
        return self.bom / self.hours

    def labour(self, rate: float) -> float:
        return self.hours * rate

    def labour_share(self, rate: float) -> float:
        total = self.bom + self.labour(rate)
        return self.labour(rate) / total if total else float("nan")


# Table 1 of the v1 manuscript, verbatim, with two stated conversions:
#   - ranges ("$80-160", "0-1 hour") are taken at their midpoint;
#   - DiSCO's "3 months" is read as 12 weeks x 40 h = 480 h at one FTE.
PROJECTS: tuple[Project, ...] = (
    Project("IvoryOS GUI control software", "IvoryOS", 0, 0, 0.5,
            "reported 0-1 h per new hardware integration; midpoint used"),
    Project("LEDbyXample modular photoreactor", "LEDbyXample", 80, 160, 24,
            "BOM range midpoint used"),
    Project("Public control of OpenFlexure microscope", "OpenFlexure control", 300, 300, 30,
            "time includes the microscope build itself"),
    Project("Science-jubilee flexible automation platform", "Science-jubilee", 2000, 2000, 100),
    Project("Powder dispensing module", "Powder dispenser", 300, 300, 10),
    Project("Rolling ball viscometer", "Rolling ball viscometer", 300, 300, 10),
    Project("Color mixing bot", "Color mixing bot", 300, 300, 10),
    Project("Digital pipette Jubilee integration", "Digital pipette", 100, 100, 3),
    Project("Electrochemical workflow on science-jubilee", "Electrochem. workflow", 20000, 20000, 300),
    Project("DiSCO photovoltaics platform", "DiSCO", 30000, 40000, 480,
            "'3 months' read as 12 weeks x 40 h = 480 h at 1 FTE"),
)


def median(values: list[float]) -> float:
    s = sorted(values)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2


def write_derived(projects: list[Project], path: Path) -> None:
    with path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(
            ["project", "bom_usd", "hours", "breakeven_wage_usd_per_h"]
            + [f"labour_usd_at_{int(r)}" for r in RATES]
            + [f"labour_share_at_{int(r)}" for r in RATES]
            + ["note"]
        )
        for p in projects:
            w.writerow(
                [p.name, f"{p.bom:.0f}", f"{p.hours:g}", f"{p.breakeven_wage:.2f}"]
                + [f"{p.labour(r):.0f}" for r in RATES]
                + [f"{p.labour_share(r):.3f}" for r in RATES]
                + [p.note]
            )


def write_sensitivity(projects: list[Project], path: Path) -> None:
    rates = [10, 15, 20, 25, 30, 40, 50, 60, 75, 100, 125, 150]
    with path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["loaded_rate_usd_per_h", "n_projects_labour_exceeds_bom",
                    "median_labour_share", "mean_labour_share"])
        for r in rates:
            shares = [p.labour_share(r) for p in projects]
            n_over = sum(1 for p in projects if p.labour(r) > p.bom)
            w.writerow([r, n_over, f"{median(shares):.3f}",
                        f"{sum(shares) / len(shares):.3f}"])


def make_figure(projects: list[Project], path: Path) -> None:
    """Two panels sharing one category axis, ordered by break-even wage.

    (a) composition of true first-build cost at a single stated rate;
    (b) the rate-free statistic: the wage at which the two halves are equal.
    """
    # Ascending break-even wage puts the largest bar at the top of (b) once
    # barh stacks index 0 at the bottom; both panels then read the same way.
    order = sorted(projects, key=lambda p: p.breakeven_wage)
    labels = [p.short for p in order]
    y = list(range(len(order)))

    fig, (ax_a, ax_b) = plt.subplots(
        1, 2, figsize=(9.6, 4.6), sharey=True,
        gridspec_kw={"width_ratios": [1.35, 1.0], "wspace": 0.32},
    )
    fig.patch.set_facecolor(SURFACE)

    # -- (a) stacked composition at $50/h ---------------------------------
    rate = 50.0
    bom_share = [1 - p.labour_share(rate) for p in order]
    lab_share = [p.labour_share(rate) for p in order]

    ax_a.barh(y, bom_share, height=0.62, color=C_BOM, zorder=3)
    # 2px surface gap between adjacent fills: draw labour with a white edge.
    ax_a.barh(y, lab_share, height=0.62, left=bom_share, color=C_LABOUR,
              zorder=3, edgecolor=SURFACE, linewidth=1.6)

    for yi, (bs, ls) in enumerate(zip(bom_share, lab_share)):
        ax_a.text(min(bs + ls / 2, 0.955), yi, f"{ls * 100:.0f}%",
                  ha="center", va="center", fontsize=8.5, color="white",
                  fontweight="bold", zorder=4)

    ax_a.set_xlim(0, 1)
    ax_a.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax_a.set_xticklabels(["0", "25", "50", "75", "100"])
    ax_a.set_xlabel("Share of true first-build cost (%)", fontsize=9, color=INK_2)
    ax_a.set_title("(a)  Where the money goes, at a $50/h loaded rate",
                   fontsize=9.5, color=INK, loc="left", pad=9)
    ax_a.axvline(0.5, color=GRID, lw=1, zorder=2)

    # -- (b) break-even wage ----------------------------------------------
    be = [p.breakeven_wage for p in order]
    ax_b.axvspan(BAND[0], BAND[1], color=GRID, alpha=0.3, zorder=1, lw=0)
    ax_b.barh(y, be, height=0.62, color=C_BOM, zorder=3)
    for yi, v in enumerate(be):
        ax_b.text(v + 1.8, yi, f"${v:,.0f}", ha="left", va="center",
                  fontsize=8.5, color=INK_2, zorder=4)

    ax_b.set_xlim(0, 88)
    ax_b.set_xticks([0, 25, 50, 75])
    ax_b.set_xticklabels(["$0", "$25", "$50", "$75"])
    ax_b.set_xlabel("Break-even wage (USD per hour)", fontsize=9, color=INK_2)
    ax_b.set_title("(b)  Where labour overtakes parts",
                   fontsize=9.5, color=INK, loc="left", pad=9)
    # Sits in the empty lower-right quadrant, clear of every bar and the title.
    ax_b.text(50, 1.4, "typical loaded rate\nfor academic personnel",
              ha="center", va="center", fontsize=7.5, color=INK_2,
              style="italic", zorder=4)

    for ax in (ax_a, ax_b):
        ax.set_yticks(y)
        ax.set_yticklabels(labels, fontsize=8.5, color=INK)
        ax.xaxis.grid(True, color=GRID, lw=0.7, zorder=0)
        ax.set_axisbelow(True)
        ax.set_facecolor(SURFACE)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color(GRID)
        ax.tick_params(length=0, colors=INK_2)

    # Identity is never colour-alone: legend present, and the labour segment
    # of every bar in (a) carries its own direct label.
    fig.legend(
        handles=[Patch(facecolor=C_BOM, label="Bill of materials"),
                 Patch(facecolor=C_LABOUR, label="Build labour")],
        loc="lower left", bbox_to_anchor=(0.075, -0.005), ncol=2,
        frameon=False, fontsize=8.5, labelcolor=INK_2, handlelength=1.4,
    )
    fig.subplots_adjust(left=0.16, right=0.975, top=0.9, bottom=0.19)

    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=300, facecolor=SURFACE)
    plt.close(fig)


def report(projects: list[Project]) -> None:
    """Print the markdown tables that go into the manuscript."""
    order = sorted(projects, key=lambda p: -p.labour_share(50.0))

    print("\n### Derived per-project table (rate = $50/h)\n")
    print("| Project | BOM (USD) | Build hours | Labour @ $50/h | Labour share | Break-even wage |")
    print("| --- | ---: | ---: | ---: | ---: | ---: |")
    for p in order:
        print(f"| {p.name} | ${p.bom:,.0f} | {p.hours:g} | ${p.labour(50):,.0f} "
              f"| {p.labour_share(50) * 100:.0f}% | ${p.breakeven_wage:,.0f}/h |")

    print("\n### Sensitivity to the assumed loaded rate\n")
    print("| Loaded rate | Projects where labour > BOM | Median labour share |")
    print("| --- | ---: | ---: |")
    for r in RATES:
        n_over = sum(1 for p in projects if p.labour(r) > p.bom)
        med = median([p.labour_share(r) for p in projects])
        print(f"| ${r:,.0f}/h | {n_over} / {len(projects)} | {med * 100:.0f}% |")

    hrs = [p.hours for p in projects]
    be = [p.breakeven_wage for p in projects]
    print("\n### Headline numbers\n")
    print(f"- Median break-even wage: ${median(be):,.0f}/h")
    print(f"- Highest break-even wage: ${max(be):,.0f}/h ("
          f"{max(projects, key=lambda p: p.breakeven_wage).short})")
    print(f"- Median replication time: {median(hrs):g} h")
    print(f"- Projects replicable in <= 100 h: "
          f"{sum(1 for h in hrs if h <= 100)} / {len(projects)}")
    print(f"- Replication time range: {min(hrs):g}-{max(hrs):g} h")


def main() -> None:
    projects = list(PROJECTS)
    write_derived(projects, HERE / "table1-derived.csv")
    write_sensitivity(projects, HERE / "sensitivity.csv")
    make_figure(projects, FIGDIR / "fig1-labour-vs-bom.png")
    report(projects)
    print(f"\nWrote table1-derived.csv, sensitivity.csv, "
          f"and {FIGDIR.name}/fig1-labour-vs-bom.png")


if __name__ == "__main__":
    main()

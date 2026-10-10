"""Figure 1 (example, one column): time against error for every salt dose.

Reads data/salt_doses.csv; writes figures/out/fig1_time_vs_error.{pdf,png}
and its caption stub.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import vcl_style as vs  # noqa: E402

vs.use("paper")
df = vs.read_csv("salt_doses.csv")
df["t_min"] = df["t_total_s"] / 60

# Context in grey, the comparison in two Okabe-Ito colours, and a marker
# shape per group so it still reads in greyscale.
GROUPS = [  # group, colour, marker, filled
    ("screening", vs.CONTEXT, "o", False),
    ("recentring", vs.CONTEXT, "s", False),
    ("hand-tuned", vs.OKABE_ITO["orange"], "D", True),
    ("optimizer", vs.OKABE_ITO["blue"], "o", True),
]

fig, ax = vs.figure("single", height_mm=58)
for group, colour, marker, filled in GROUPS:
    g = df[df["group"] == group]
    ax.scatter(g["t_min"], g["abs_error_mg"], s=12, marker=marker, linewidths=vs.LINE_PT,
               facecolors=colour if filled else "none", edgecolors=colour, label=group,
               zorder=3 if filled else 2)
ax.set_yscale("log")
ax.set_xlim(0, 7)
ax.set_ylim(0.3, 150)
ax.set_yticks([1, 10, 100], ["1", "10", "100"])
ax.minorticks_off()
ax.set_xlabel(vs.qty("Time per dose", "min"))
ax.set_ylabel(vs.qty("Absolute error", "mg"))
ax.legend(loc="upper right", ncols=2, handletextpad=0.2, columnspacing=0.8)

vs.save(fig)
vs.caption(
    what="Time per 0.5 g dose of salt against its absolute error, for every dose of the "
         "campaign, by how its settings were chosen",
    n={g: int((df["group"] == g).sum()) for g, *_ in GROUPS},
    error_bars="none: each point is a single dose",
    data="salt_doses.csv",
)

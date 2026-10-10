"""Figure 2 (example, two columns): error and time per group of salt doses.

Reads data/salt_doses.csv; writes figures/out/fig2_group_spread.{pdf,png}
and its caption stub.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import vcl_style as vs  # noqa: E402

vs.use("paper")
df = vs.read_csv("salt_doses.csv")
ok = df[df["status"] == "ok"].copy()          # overshoots end in seconds and would look fast
ok["t_min"] = ok["t_total_s"] / 60

ORDER = ["hand-tuned", "screening", "recentring", "optimizer"]
COLOUR = {"hand-tuned": vs.OKABE_ITO["orange"], "screening": vs.CONTEXT,
          "recentring": vs.CONTEXT, "optimizer": vs.OKABE_ITO["blue"]}
rng = np.random.default_rng(0)                # fixed jitter, so the figure rebuilds identically

fig, axes = vs.figure("double", height_mm=62, ncols=2)
for ax, col, label, letter in zip(axes, ["abs_error_mg", "t_min"],
                                  [vs.qty("Absolute error", "mg"), vs.qty("Time per dose", "min")],
                                  "ab"):
    for i, group in enumerate(ORDER):
        y = ok.loc[ok["group"] == group, col].to_numpy()
        x = i + rng.uniform(-0.12, 0.12, y.size)
        ax.scatter(x, y, s=8, facecolors="none", edgecolors=COLOUR[group], linewidths=vs.LINE_PT,
                   zorder=2)
        ax.errorbar(i + 0.32, y.mean(), yerr=y.std(ddof=1), fmt="o", ms=3.5,
                    color=COLOUR[group], zorder=3)
    ax.set_xticks(range(len(ORDER)), ORDER)
    ax.set_xlim(-0.5, len(ORDER) - 0.3)
    ax.set_ylim(bottom=0)
    ax.set_ylabel(label)
    vs.panel_label(ax, letter)

vs.save(fig)
vs.caption(
    what="Absolute error (a) and time (b) of the salt doses that ended within tolerance "
         "and inside the time limit, by how their settings were chosen. Open circles are "
         "single doses; each group's settings differ from dose to dose, so the spread is "
         "across settings, not repeatability",
    n={g: int((ok["group"] == g).sum()) for g in ORDER},
    error_bars="mean ± one standard deviation of the doses in the group",
    data="salt_doses.csv",
)

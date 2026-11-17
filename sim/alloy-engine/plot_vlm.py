"""Chart of out/vlm_tray_sweep.json: what each loose item did at each tray acceleration, against the textbook onset."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

OUT = Path(__file__).resolve().parent / "out"
d = json.loads((OUT / "vlm_tray_sweep.json").read_text())
A = np.array(d["accels"])
edges = np.sqrt(A[1:] * A[:-1])
edges = np.concatenate([[A[0] ** 2 / edges[0]], edges, [A[-1] ** 2 / edges[-1]]])
# held: neutral; slid / tipped over / off the tray: the first three categorical slots (validated all-pairs, light);
# rocked (tilted over 5 degrees, then stood back up): a darker neutral. Every coloured cell also carries a glyph.
OUTCOMES = [("held", "#ebeae6", ""), ("slid", "#2a78d6", "s"), ("rocked", "#8d8b85", "r"),
            ("fell", "#eb6834", "X"), ("off", "#1baf7a", "o")]
LABEL = {"held": "held", "slid": "slid (s)", "rocked": "rocked, stood back up (r)", "fell": "tipped over (X)",
         "off": "slid off the tray (o)"}
code = {o: i for i, (o, _, _) in enumerate(OUTCOMES)}
cmap = ListedColormap([c for _, c, _ in OUTCOMES])
items = [it["name"] for it in d["items"]]
labels = {it["name"]: it["label"] for it in d["items"]}
INK, MUTED = "#0b0b0b", "#52514e"

fig, axes = plt.subplots(2, 1, figsize=(11, 6.6), sharex=True, gridspec_kw={"hspace": 0.32})
for ax, surf in zip(axes, d["surfaces"]):
    grid = np.zeros((len(items), len(A)), dtype=int)
    for r in d["rows"]:
        if r["surface"] == surf["name"]:
            grid[items.index(r["item"]), int(np.argmin(np.abs(A - r["accel"])))] = code[r["outcome"]]
    ax.pcolormesh(edges, np.arange(len(items) + 1), grid, cmap=cmap, vmin=-0.5, vmax=len(OUTCOMES) - 0.5,
                  edgecolors="#fcfcfb", linewidth=1.0)
    for i in range(len(items)):
        for j in range(len(A)):
            g = OUTCOMES[grid[i, j]][2]
            if g:
                ax.text(A[j], i + 0.5, g, ha="center", va="center", fontsize=6.5, color="white", fontweight="bold")
        t = d["thresholds"][f"{surf['name']}/{items[i]}"]
        a0 = min(t["a_slide"], t["a_tip"])
        if a0 < A[-1]:
            ax.plot([a0, a0], [i + 0.06, i + 0.94], color=INK, lw=2.0, solid_capstyle="butt")
            ax.text(a0 * 1.02, i + 0.80, "μg" if t["first"] == "slide" else "g·D/H", fontsize=7, color=INK,
                    ha="left", va="center", bbox=dict(fc="white", ec="none", pad=0.4, alpha=0.85))
    ax.axvline(0.3, color=MUTED, lw=1, ls=(0, (3, 2)))
    ax.set_yticks(np.arange(len(items)) + 0.5, [labels[n] for n in items], fontsize=9, color=INK)
    ax.set_ylim(len(items), 0)
    mus = sorted({round(d["thresholds"][f"{surf['name']}/{n}"]["mu"], 2) for n in items})
    ax.set_title(f"{surf['label'].capitalize()} tray (μ = {mus[0]:.2f}–{mus[-1]:.2f} from Alloy's material cards)",
                 loc="left", fontsize=10.5, color=INK)
    ax.tick_params(colors=MUTED, length=0)
    for s in ax.spines.values():
        s.set_visible(False)
ax = axes[-1]
ax.set_xscale("log")
ticks = [0.3, 0.5, 1, 2, 3, 5, 10]
ax.set_xticks(ticks, [f"{t:g}" for t in ticks])
ax.set_xlim(edges[0], edges[-1])
ax.set_xlabel("Tray acceleration and braking, m/s² (one world each; 0.4 s speeding up, 0.4 s slowing down)",
              fontsize=9.5, color=INK)
handles = [Patch(fc=c, ec="none", label=LABEL[o]) for o, c, _ in OUTCOMES]
handles.append(plt.Line2D([], [], color=INK, lw=2, label="textbook onset: slides at μg or tips at g·D/H, whichever is lower"))
handles.append(plt.Line2D([], [], color=MUTED, lw=1, ls=(0, (3, 2)), label="MiR250's published 0.3 m/s²"))
fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.125, 0.995), ncol=4, frameon=False, fontsize=8.5)
fig.suptitle("")
fig.text(0.125, 1.035, f"Loose labware on a moving VLM tray: Alloy {d['alloy_version']}, {d['worlds']} parallel worlds "
         f"on one CPU core ({d['run_s']:.0f} s)", fontsize=12.5, color=INK, ha="left")
fig.savefig(OUT / "vlm_tray_sweep.png", dpi=150, bbox_inches="tight", facecolor="#fcfcfb")
print("wrote", OUT / "vlm_tray_sweep.png")

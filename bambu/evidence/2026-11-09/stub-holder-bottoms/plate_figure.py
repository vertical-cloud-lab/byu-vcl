"""Top view of the sliced plate (walls at z = 10 mm) and a close-up of one pin hole per part."""
import json, math, re, sys, zipfile
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Circle, Rectangle
import numpy as np

src, holes_json, out = sys.argv[1:4]
SURF, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
C = {"3.3": "#2a78d6", "3.4": "#eb6834"}   # categorical slots 1 and 2, validated
g = zipfile.ZipFile(src).read("Metadata/plate_1.gcode").decode().splitlines()

# walls of the layer nearest z = 10 mm, as polylines (arcs sampled)
segs = {"3.3": [], "3.4": []}
x = y = None; lz = None; feat = None; cur = None
def flush():
    global cur
    if cur and len(cur) > 1:
        P = np.array(cur); segs["3.3" if P[:, 1].mean() < 90 else "3.4"].append(P)
    cur = None
for line in g:
    if line.startswith("; Z_HEIGHT:"):
        flush(); lz = round(float(line.split(":")[1]), 2)
    elif line.startswith("; FEATURE:"):
        flush(); feat = line.split(":", 1)[1].strip()
    elif line[:3] in ("G1 ", "G0 ", "G2 ", "G3 "):
        m = dict(re.findall(r"([XYEIJ])(-?[\d.]+)", line.split(";")[0]))
        nx = float(m["X"]) if "X" in m else x; ny = float(m["Y"]) if "Y" in m else y
        extr = "E" in m and float(m["E"]) > 0 and (nx, ny) != (x, y)
        if extr and lz == 10.0 and feat in ("Outer wall", "Inner wall"):
            if cur is None: cur = [(x, y)]
            if line[:2] in ("G2", "G3"):
                cx, cy = x + float(m.get("I", 0)), y + float(m.get("J", 0)); r = math.hypot(x - cx, y - cy)
                a0 = math.atan2(y - cy, x - cx); a1 = math.atan2(ny - cy, nx - cx)
                if line[:2] == "G2":
                    while a1 >= a0: a1 -= 2 * math.pi
                else:
                    while a1 <= a0: a1 += 2 * math.pi
                for t in np.linspace(0, 1, 24)[1:]:
                    a = a0 + (a1 - a0) * t; cur.append((cx + r * math.cos(a), cy + r * math.sin(a)))
            else:
                cur.append((nx, ny))
        else:
            flush()
        x, y = nx, ny
flush()

S = json.load(open(holes_json))["summary"]
on = S["circle_compensation_on (stub_holder_bottoms_A1mini_blackPLA.gcode.3mf)"]
off = S["stock, compensation off (report_stock.json)"]

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "text.color": INK,
                     "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED})
fig = plt.figure(figsize=(11.5, 5.6), facecolor=SURF)
gs = fig.add_gridspec(2, 2, width_ratios=[1.35, 1], wspace=0.18, hspace=0.32)
ax = fig.add_subplot(gs[:, 0], facecolor=SURF)
ax.add_patch(Rectangle((0, 0), 180, 180, fill=False, ec=MUTED, lw=1))
for part, polys in segs.items():
    for P in polys:
        ax.plot(P[:, 0], P[:, 1], color=C[part], lw=1.0, solid_capstyle="round")
ax.text(90, 47.5 - 4, "Bottom 3.3: Ø3.3 mm holes, at the FRONT", ha="center", va="top", color=INK, fontsize=10)
ax.text(90, 130 + 4, "Bottom 3.4: Ø3.4 mm holes, at the BACK", ha="center", va="bottom", color=INK, fontsize=10)
ax.annotate("front of the printer", xy=(90, 1), xytext=(90, 16), ha="center", va="bottom", color=INK2,
            arrowprops=dict(arrowstyle="-|>", color=INK2, lw=1))
ax.set_xlim(-4, 184); ax.set_ylim(-6, 184); ax.set_aspect("equal")
ax.set_xlabel("X on the bed (mm)"); ax.set_ylabel("Y on the bed (mm)")
ax.set_xticks([0, 45, 90, 135, 180]); ax.set_yticks([0, 45, 90, 135, 180])
for s in ax.spines.values(): s.set_visible(False)
ax.set_title("A1 mini plate, walls at z = 10 mm (Bambu Studio CLI slice)", loc="left", fontsize=11, color=INK)
from matplotlib.lines import Line2D
ax.legend(handles=[Line2D([], [], color=C["3.3"], lw=2, label="Bottom 3.3"), Line2D([], [], color=C["3.4"], lw=2, label="Bottom 3.4")],
          loc="upper right", frameon=False, fontsize=9)

for row, part in enumerate(("3.3", "3.4")):
    a = fig.add_subplot(gs[row, 1], facecolor=SURF)
    r_cad = float(part) / 2
    r_on = on[f"Bottom {part}"]["outer_wall_path_radius_mm"]; r_off = off[f"Bottom {part}"]["outer_wall_path_radius_mm"]
    a.add_patch(Wedge((0, 0), r_on + 0.21, 0, 360, width=0.42, fc=C[part], ec="none", alpha=0.85))
    a.add_patch(Circle((0, 0), r_cad, fill=False, ec=INK, lw=1.2))
    a.set_xlim(-2.6, 5.9); a.set_ylim(-2.6, 2.6); a.set_aspect("equal"); a.axis("off")
    aim = 2 * (r_on - 0.21)
    a.text(2.75, 1.55, f"Bottom {part}, one of its 8 holes", color=INK, fontsize=10, va="center")
    a.text(2.75, 0.75, f"black circle: Onshape, Ø{part} mm", color=INK2, fontsize=9, va="center")
    a.text(2.75, 0.05, f"filled ring: outer wall, compensation on;\nthe hole it leaves is Ø{aim:.2f} mm", color=INK2, fontsize=9, va="center")
    a.text(2.75, -1.0, f"with compensation off, the wall's inside\nedge sits on the black circle (Ø{2 * (r_off - 0.21):.2f} mm)", color=INK2, fontsize=9, va="center")
fig.text(0.535, 0.015, "Toolpath sizes, not printed sizes: holes in PLA usually print 0.2-0.4 mm smaller than the path aims.",
         color=MUTED, fontsize=8.5)
fig.savefig(out, dpi=130, facecolor=SURF, bbox_inches="tight")
print("wrote", out)

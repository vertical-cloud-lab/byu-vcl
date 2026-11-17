"""Chart and GIF of the doser_funnel.py runs found in out/: powder in the vial over time, and what stays in the funnel."""
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def save_gif(frames, path, ms, scale=0.8, step=1, hold=10):
    """Every `step`-th frame, scaled and put on one shared 128-colour palette, so the GIF stays a few MB."""
    frames = frames[::step] + ([frames[-1]] if (len(frames) - 1) % step else [])
    size = (int(frames[0].width * scale), int(frames[0].height * scale))
    small = [f.resize(size, Image.LANCZOS) for f in frames]
    pal = small[len(small) // 2].convert("P", palette=Image.ADAPTIVE, colors=128)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in small]
    q[0].save(path, save_all=True, append_images=q[1:] + [q[-1]] * hold, duration=ms, loop=0, optimize=True)

OUT = Path(__file__).resolve().parent / "out"
runs = sorted((json.loads(p.read_text()) for p in OUT.glob("doser_funnel_b*.json")), key=lambda r: r["beta_deg"])
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]          # categorical slots 1-4, fixed order
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
mu_w = runs[0]["mu_wall"]
phi_w = math.degrees(math.atan(mu_w))
SPACING = 0.0015                                               # m: half the 3 mm MPM voxel Alloy picked
RHO_BULK = 0.59 * 2650.0                                       # Alloy fills grains at packing 0.59 x grain density
grams = runs[0]["particles"] * RHO_BULK * SPACING ** 3 * 1000

fig, (ax, bx) = plt.subplots(1, 2, figsize=(11, 4.2), gridspec_kw={"width_ratios": [1.7, 1], "wspace": 0.28})
ends = []
for r, c in zip(runs, SERIES):
    t = [e["t"] for e in r["log"]]
    y = [100 * e["in_vial"] for e in r["log"]]
    ax.plot(t, y, color=c, lw=2)
    ends.append([y[-1], t[-1], f"{r['beta_deg']:g}°", c])
ends.sort(key=lambda e: -e[0])                       # direct labels, pushed apart so none overlap
for k in range(1, len(ends)):
    ends[k][0] = min(ends[k][0], ends[k - 1][0] - 6)
for y, t, label, c in ends:
    ax.text(t + 0.03, y, label, color=INK, fontsize=9, va="center")
ax.set_xlim(0, max(r["log"][-1]["t"] for r in runs) + 0.18)
ax.set_ylim(0, 105)
ax.set_xlabel("time since the powder was let go, s", color=INK, fontsize=9.5)
ax.set_ylabel("powder in the vial, % of the dose", color=INK, fontsize=9.5)
ax.set_title(f"Each line: one funnel wall angle (from horizontal); {grams:.1f} g dose", loc="left", fontsize=10,
             color=INK)
ax.grid(color=GRID, lw=0.8)
ax.set_axisbelow(True)
holdup = [100 * r["log"][-1]["in_funnel"] for r in runs]
betas = [r["beta_deg"] for r in runs]
bx.axvspan(0, phi_w, color="#f0efec", lw=0)
bx.axvline(phi_w, color=MUTED, lw=1, ls=(0, (3, 2)))
bx.text(phi_w + 1, 52, f"wall friction angle\natan(μw = {mu_w:.2f}) = {phi_w:.1f}°", fontsize=8, color=MUTED, va="top")
for b, h, c in zip(betas, holdup, SERIES):
    bx.plot([b, b], [0, h], color=c, lw=2, solid_capstyle="butt")
    bx.plot([b], [h], "o", ms=8, color=c, mec="#fcfcfb", mew=2)
    bx.text(b + 1.5, h + 1.5, f"{h:.0f} %", fontsize=9, color=INK)
bx.set_xlim(0, 65)
bx.set_ylim(0, 55)
bx.set_xlabel("funnel wall angle from horizontal, °", color=INK, fontsize=9.5)
bx.set_ylabel(f"left in the funnel at {runs[0]['log'][-1]['t']:g} s, %", color=INK, fontsize=9.5)
bx.set_title("What the funnel holds back", loc="left", fontsize=10, color=INK)
bx.grid(axis="y", color=GRID, lw=0.8)
bx.set_axisbelow(True)
for a in (ax, bx):
    a.tick_params(colors=MUTED, length=0)
    for s in a.spines.values():
        s.set_visible(False)
fig.text(0.125, 1.0, f"Powder through the doser's funnel: Alloy {runs[0]['alloy_version']}, sand on Newton's MPM solver, "
         f"CPU ({runs[0]['particles']:,} particles)", fontsize=12, color=INK, ha="left")
fig.savefig(OUT / "doser_funnel.png", dpi=150, bbox_inches="tight", facecolor="#fcfcfb")
print("wrote", OUT / "doser_funnel.png", "holdup", dict(zip(betas, holdup)), f"dose {grams:.2f} g")

# GIF: the four runs side by side, frame for frame (every run rendered at the same times)
stacks = [np.load(OUT / f"doser_funnel_b{b:g}_frames.npy") for b in betas
          if (OUT / f"doser_funnel_b{b:g}_frames.npy").exists()]
if stacks:
    n = min(len(s) for s in stacks)
    h, w = stacks[0].shape[1:3]
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 16)
        small = ImageFont.truetype("DejaVuSans.ttf", 12)
    except OSError:
        font = small = ImageFont.load_default()
    dt = runs[0]["log"][1]["t"] - runs[0]["log"][0]["t"]
    frames = []
    for i in range(n):
        sheet = Image.new("RGB", (w * len(stacks), h), "white")
        for j, (s, r) in enumerate(zip(stacks, runs)):
            im = Image.fromarray(s[i])
            d = ImageDraw.Draw(im)
            d.text((10, 8), f"wall {r['beta_deg']:g}° from horizontal", fill=INK, font=font)
            e = r["log"][min(i, len(r["log"]) - 1)]
            d.text((10, 30), f"t = {i * dt:.2f} s   in vial {100 * e['in_vial']:.0f} %", fill=MUTED, font=small)
            sheet.paste(im, (j * w, 0))
        frames.append(sheet)
    save_gif(frames, OUT / "doser_funnel.gif", ms=100, scale=0.8, step=1)
    frames[min(6, n - 1)].save(OUT / "doser_funnel_frame.png")
    frames[-1].save(OUT / "doser_funnel_final.png")
    print("wrote", OUT / "doser_funnel.gif", n, "frames")

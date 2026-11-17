"""Chart and GIF of the doser_pour.py runs in out/: the load cell's reading against time, and each dose's error."""
import json
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
runs = [json.loads(p.read_text()) for p in sorted(OUT.glob("doser_pour_t*_a*.json")) if not p.name.endswith("frames.json")]
for r in runs:
    r["pass"] = (r["allow_g"], r.get("allow_rate_s", 0.0))
targets = sorted({r["target_g"] for r in runs})
allows = sorted({r["pass"] for r in runs})              # one entry per pass: (allowance g, allowance s x flow)


def name(a):
    return "no allowance" if a == (0.0, 0.0) else f"allowance {a[0]:g} g + {a[1]:g} s × flow"


def stem(tg, a):
    return f"doser_pour_t{tg:g}_a{a[0]:g}" + (f"_r{a[1]:g}" if a[1] else "")
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]                  # one colour per target: categorical slots 1-3
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
color = dict(zip(targets, SERIES))
style = {a: ("solid" if a == max(allows) and len(allows) > 1 else (0, (4, 2)) if len(allows) > 1 else "solid")
         for a in allows}

fig, (ax, bx) = plt.subplots(1, 2, figsize=(11, 4.3), gridspec_kw={"width_ratios": [1.8, 1], "wspace": 0.25})
for r in sorted(runs, key=lambda r: (r["pass"], r["target_g"])):
    t = np.array([e["t"] for e in r["log"]])
    g = np.array([e["grams"] for e in r["log"]])
    c = color[r["target_g"]]
    ax.plot(t, g, color=c, lw=2 if style[r["pass"]] == "solid" else 1.4, ls=style[r["pass"]])
    if r["t_stop"] is not None:
        i = int(round(r["t_stop"] * 100))
        ax.plot([t[i]], [g[i]], "o", ms=7, color=c, mec="#fcfcfb", mew=2)
for tg in targets:
    ax.axhline(tg, color=MUTED, lw=0.8, ls=(0, (1, 2)))
    ax.text(0.02, tg + 0.12, f"target {tg:g} g", fontsize=8, color=MUTED)
ax.set_xlabel("time, s", color=INK, fontsize=9.5)
ax.set_ylabel("load cell reading, g (powder in the vial)", color=INK, fontsize=9.5)
ax.set_title("Load cell reading, one colour per target", loc="left", fontsize=9.5, color=INK)
handles = [plt.Line2D([], [], color=MUTED, lw=2 if style[a] == "solid" else 1.4, ls=style[a], label=name(a))
           for a in allows]
handles.append(plt.Line2D([], [], color=MUTED, lw=0, marker="o", ms=7, mec="#fcfcfb", mew=2,
                          label="the scoop starts tipping back"))
ax.legend(handles=handles, loc="lower right", frameon=False, fontsize=8.5)
ax.grid(color=GRID, lw=0.8)
ax.set_axisbelow(True)
for k, a in enumerate(allows):
    xs = np.arange(len(targets)) + (k - (len(allows) - 1) / 2) * 0.22
    for x, tg in zip(xs, targets):
        r = next((r for r in runs if r["target_g"] == tg and r["pass"] == a), None)
        if r is None:
            continue
        e = r["final_g"] - tg
        bx.plot([x, x], [0, e], color=color[tg], lw=2, ls=style[a] if len(allows) > 1 else "solid")
        bx.plot([x], [e], "o", ms=8, color=color[tg], mec="#fcfcfb", mew=2)
        bx.text(x + 0.05, e, f"{e:+.2f}", fontsize=8.5, color=INK, va="center")
bx.axhline(0, color=INK, lw=0.8)
bx.set_xticks(range(len(targets)), [f"{tg:g} g" for tg in targets])
bx.set_xlim(-0.6, len(targets) - 0.3)
bx.set_ylabel("dose − target, g", color=INK, fontsize=9.5)
sub = "Each dose's error" + (" (dashed: no allowance)" if len(allows) > 1 else "")
bx.set_title(sub, loc="left", fontsize=9.5, color=INK)
bx.grid(axis="y", color=GRID, lw=0.8)
bx.set_axisbelow(True)
for a in (ax, bx):
    a.tick_params(colors=MUTED, length=0)
    for s in a.spines.values():
        s.set_visible(False)
r0 = runs[0]
fig.text(0.125, 1.0, f"Powder, dosed to the mark: a scoop tips {r0['powder_g']:.1f} g of powder into a vial on a load cell "
         f"(Alloy {r0['alloy_version']}, MPM, CPU)", fontsize=12, color=INK, ha="left")
fig.savefig(OUT / "doser_pour.png", dpi=150, bbox_inches="tight", facecolor="#fcfcfb")
print("wrote", OUT / "doser_pour.png")
for r in sorted(runs, key=lambda r: (r["pass"], r["target_g"])):
    print(f"target {r['target_g']:g} {name(r['pass'])}: stop reading {r['stop_reading_g']}, final {r['final_g']:.3f}, "
          f"error {r['final_g'] - r['target_g']:+.3f} g, t_stop {r['t_stop']}, wall {r['wall_s']} s, ok {r['health_ok']}")

# GIF of one pass (the last one with frames), the targets side by side
stacks = []
for a in reversed(allows):
    stacks = [(tg, np.load(OUT / f"{stem(tg, a)}_frames.npy"), json.loads((OUT / f"{stem(tg, a)}_frames.json").read_text()))
              for tg in targets if (OUT / f"{stem(tg, a)}_frames.npy").exists()]
    if stacks:
        break
if stacks:
    n = max(len(s) for _, s, _ in stacks)
    h, w = stacks[0][1].shape[1:3]
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 16)
        small = ImageFont.truetype("DejaVuSans.ttf", 12)
    except OSError:
        font = small = ImageFont.load_default()
    frames = []
    for i in range(n):
        sheet = Image.new("RGB", (w * len(stacks), h), "white")
        for j, (tg, s, meta) in enumerate(stacks):
            k = min(i, len(s) - 1)
            im = Image.fromarray(s[k])
            d = ImageDraw.Draw(im)
            m = meta[k]
            d.text((10, 8), f"target {tg:g} g", fill=INK, font=font)
            d.text((10, 30), f"load cell {m['grams']:.2f} g", fill=INK, font=font)
            d.text((10, 54), f"t = {m['t']:.2f} s   tilt {m['theta_deg']:.0f}°   {m['phase']}", fill=MUTED, font=small)
            sheet.paste(im, (j * w, 0))
        frames.append(sheet)
    save_gif(frames, OUT / "doser_pour.gif", ms=100, scale=0.8, step=2)
    frames[len(frames) // 2].save(OUT / "doser_pour_frame.png")
    print("wrote", OUT / "doser_pour.gif", n, "frames")

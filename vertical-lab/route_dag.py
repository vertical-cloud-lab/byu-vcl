"""The alloy route as a function network: the DAG from DAL's ONR YIP figures, brought in one stage at a time before each
chapter of the alloy route (byu-vcl #303, PR #318).

    python3 route_dag.py          # -> out/dag/route_dag_ch{1..5}.png and .mp4, out/dag/route_dag_sheet.png, out/dag/route_dag.json

Asked for on PR #318 (2026-11-04): "For the alloy workflow, you should bring in some version of the DAG either from the
Cu YIP proposal or the Genesis Mission FLAIME proposal, both from DAL repo; showing the progression of steps. This will
probably need to have some gradual introduction of steps (and removal of prior, no longer prioritized/focused on text)
so the viewer doesn't get overloaded with information."

**The graph is DAL's, unchanged.** digital-alloy-lab, branch ``onr-yip-figs-oct27-integrate`` at ``b553306``,
``benchmarks/bofn-prelim/dag/network_dag.py`` and its README: the function network behind the BOFN preliminary results
in the ONR YIP figures. Inputs (composition), CALPHAD ($10, one call returns three outputs), Atomize ($1,500 a run),
Print ($2,500 a build), Test ($200 a bar), and the objective (strength less 0.3 x the critical-mineral burden). The
node labels, the edges and the costs are that file's; the layout follows its columns. FLAIME's DAG (the DOE Genesis
proposal, ``benchmarks/figures/bofn_dag.png`` on main) is the same chain with four coarser nodes and other costs, so the
YIP's is the one used. DAL's benchmark composition is Zn+Mg, Cu, Zr, Sc; the route animated here makes Al-10Si, so the
input box names both.

**What is added** is the lab's own five steps as a row of chips under the graph, each under the stage it serves, and,
for chapter 5, which instrument looks at which node. Those are this repository's mapping, not DAL's.

**How it is introduced.** Each chapter's card shows only the stages reached so far. The stage the chapter is about is
red, earlier stages fade to grey, and later ones aren't drawn yet. One caption at a time: each replaces the last.
"""
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402
from matplotlib.path import Path as MPath  # noqa: E402
from PIL import Image  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "out" / "dag"
SOURCE = ("digital-alloy-lab, onr-yip-figs-oct27-integrate @ b553306, benchmarks/bofn-prelim/dag/network_dag.py",
          "https://github.com/vertical-cloud-lab/digital-alloy-lab/blob/b553306/benchmarks/bofn-prelim/dag/network_dag.py")

for f in ("/usr/share/fonts/truetype/lato/Lato-Regular.ttf", "/usr/share/fonts/truetype/lato/Lato-Bold.ttf"):
    if Path(f).exists():
        font_manager.fontManager.addfont(f)
plt.rcParams.update({"font.family": ["Lato", "DejaVu Sans"]})

# DAL's deck palette (network_dag.py)
INK, GRAY, LIGHT, FAINT = "#1A1A1A", "#7F7F7F", "#BFBFBF", "#D9D9D9"
RED = "#E00000"
NODE_FILL, NODE_LINE, EDGE = "#F4F4F4", "#595959", "#404040"
WHITE = "#FFFFFF"

W, H, DPI = 12.8, 7.2, 100            # 1280 x 720
COLS = ["I", "C", "A", "L", "T", "O"]
HEADERS = {"I": "Inputs", "C": "CALPHAD", "A": "Atomize", "L": "Print", "T": "Test", "O": "Objective"}
COSTS = {"C": "$10", "A": "$1,500", "L": "$2,500", "T": "$200"}      # DAL's COSTS, per call / run / build / bar
BOX_W, BOX_H, IN_H, MARGIN = 1.62, 0.80, 0.56, 0.32
GAP = (W - 2 * MARGIN - len(COLS) * BOX_W) / (len(COLS) - 1)
COL_X = {c: MARGIN + i * (BOX_W + GAP) for i, c in enumerate(COLS)}
HEADER_Y = 0.62

# node -> (label, column, row centre in inches from the top): DAL's NODES, rows compressed to make room for the chips
NODES = {"s": ("Strengthening\nphase fraction", "C", 1.50), "f": ("Freezing\nrange", "C", 2.45),
         "g": ("Nucleant\nfraction", "C", 3.40), "q": ("Powder\nquality", "A", 4.45),
         "rho": ("Dense,\ncrack-free\nfraction", "L", 3.75), "U": ("Strength", "T", 2.62),
         "OBJ": ("Strength\n− 0.3 × burden", "O", 2.62)}
INPUTS = {"comp": ("Composition\nDAL: Zn+Mg, Cu, Zr, Sc\nhere: Al-10Si", "I", 2.45),
          "a": ("Atomizer\nsetting", "A", 5.38), "pv": ("Laser power,\nscan speed", "L", 4.70)}
STAGE_OF = {"comp": "I", "s": "C", "f": "C", "g": "C", "q": "A", "a": "A", "rho": "L", "pv": "L", "U": "T", "OBJ": "O"}
# DAL's edges (SPEC parents, plus U -> objective); inputs enter from the left ("comp") or from below ("a", "pv")
EDGES = [("comp", "s"), ("comp", "f"), ("comp", "g"), ("g", "q"), ("a", "q"), ("f", "rho"), ("g", "rho"),
         ("q", "rho"), ("pv", "rho"), ("s", "U"), ("rho", "U"), ("U", "OBJ")]
FROM_BELOW = {"a", "pv"}

# the lab's five steps (this repository's chapters), each under the stage it serves
CHIPS = [("1", "Charge cups", "A"), ("2", "Melt + atomize", "A"), ("3", "Sieve + print", "L"),
         ("4", "Depowder, cut, pull", "T"), ("5", "Characterize", "T")]
CHIP_Y, CHIP_H, CHIP_W = 6.08, 0.42, 2.18
CAPTION_Y = 6.82
# chapter 5: which instrument looks at which node (this repository's mapping)
LOOKS = {"q": "Mastersizer: size distribution", "rho": "SEM, OpenFlexure: pores, cracks",
         "U": "PIP, nanoindenter, Vickers:\nstrength without a bar"}

# Each beat: (stages drawn, the stage in red, red chips, extra red nodes, caption). Stages before the red one are grey.
BEATS = {
    1: [(["I"], "I", [], [], "A design starts as a composition."),
        (["I", "C"], "C", [], [], "CALPHAD screens it first: one $10 call returns three numbers."),
        (["I", "C", "A"], "A", ["1"], ["comp"],
         "Chapter 1: the composition becomes charge cups, dosed, weighed and pressed.")],
    2: [(["I", "C", "A"], "A", ["2"], ["q", "a"], "Chapter 2: melt and atomize. Its output is powder quality.")],
    3: [(["I", "C", "A", "L"], "L", ["3"], [], "Chapter 3: sieve the powder and print. Is the build dense and crack-free?")],
    4: [(["I", "C", "A", "L", "T", "O"], "T", ["4"], ["U", "OBJ"], "Chapter 4: cut a bar and pull it. Strength is what the "
         "objective scores.")],
    5: [(["I", "C", "A", "L", "T", "O"], None, ["5"], ["q", "rho", "U"],
         "Chapter 5: cheaper looks at the same nodes, from the trays.")],
}
TITLE = "The alloy route as a function network"
SUB = "DAL's ONR YIP network (network_dag.py): a column per stage, its cost above it"


def rect(key):
    label, col, yc = (NODES.get(key) or INPUTS[key])
    h = IN_H if key in INPUTS and key != "comp" else (1.10 if key == "comp" else BOX_H)
    return COL_X[col], yc - h / 2, BOX_W, h


def tone_of(key, drawn, red, red_nodes):
    """red: the chapter's focus; normal: drawn, not in focus; faint: an earlier stage; None: not reached yet."""
    st = STAGE_OF[key]
    if st not in drawn or (red is None and key in FROM_BELOW):     # chapter 5: the settings aren't the point
        return None
    if key in red_nodes or (st == red and not red_nodes):
        return "red"
    if red is not None and st == red:
        return "normal"
    if red is not None and COLS.index(st) > COLS.index(red):
        return "normal"
    return "faint"


def draw(ch, beat, path):
    drawn, red, chips_red, red_nodes, caption = beat
    fig = plt.figure(figsize=(W, H), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")
    fig.patch.set_facecolor(WHITE)
    ax.text(MARGIN, 0.14, TITLE, fontsize=15, color=INK, fontweight="bold", va="top")
    ax.text(W - MARGIN, 0.16, SUB, fontsize=9.5, color=GRAY, va="top", ha="right")
    line = {"red": RED, "normal": NODE_LINE, "faint": FAINT}
    text = {"red": INK, "normal": INK, "faint": LIGHT}
    edge = {"red": RED, "normal": EDGE, "faint": FAINT}
    tones = {k: tone_of(k, drawn, red, red_nodes) for k in list(NODES) + list(INPUTS)}
    for c in COLS:
        if c not in drawn:
            continue
        if red is None:
            t = "normal"
        else:
            t = "red" if c == red else ("faint" if COLS.index(c) < COLS.index(red) else "normal")
        s = HEADERS[c] + (f"  {COSTS[c]}" if c in COSTS else "")
        ax.text(COL_X[c] + BOX_W / 2, HEADER_Y, s, fontsize=15, color={"red": RED, "normal": GRAY, "faint": LIGHT}[t],
                ha="center", va="center", fontweight="bold" if t == "red" else "normal")
    if "C" in drawn:                                       # CALPHAD's one call returns all three
        t = "red" if red == "C" else "faint"
        x, y0 = COL_X["C"] - 0.08, NODES["s"][2] - BOX_H / 2 - 0.10
        y1 = NODES["g"][2] + BOX_H / 2 + 0.24
        ax.add_patch(FancyBboxPatch((x, y0), BOX_W + 0.16, y1 - y0, boxstyle="round,pad=0,rounding_size=0.12",
                                    fill=False, ec=line[t], lw=1.2, ls=(0, (4, 3)), zorder=2))
        ax.text(x + BOX_W + 0.10, y1 - 0.05, "one call", fontsize=9, color=line[t], ha="right", va="bottom")
    for a, b in EDGES:
        ta, tb = tones[a], tones[b]
        if ta is None or tb is None:
            continue
        if red is None:
            t = "faint"
        else:
            t = "red" if tb == "red" else ("faint" if "faint" in (ta, tb) else "normal")
        xa, ya, wa, ha = rect(a)
        xb, yb, wb, hb = rect(b)
        if a in FROM_BELOW:
            verts, codes = [(xa + wa / 2, ya), (xb + wb / 2, yb + hb)], [MPath.MOVETO, MPath.LINETO]
        else:
            p0, p1 = (xa + wa, ya + ha / 2), (xb, yb + hb / 2)
            dx = (p1[0] - p0[0]) * 0.5
            verts = [p0, (p0[0] + dx, p0[1]), (p1[0] - dx, p1[1]), p1]
            codes = [MPath.MOVETO, MPath.CURVE4, MPath.CURVE4, MPath.CURVE4]
        ax.add_patch(FancyArrowPatch(path=MPath(verts, codes), arrowstyle="-|>", mutation_scale=13,
                                     color=edge[t], lw=1.7 if t == "red" else 1.3, zorder=2))
    for k in list(NODES) + list(INPUTS):
        t = tones[k]
        if t is None:
            continue
        x, y, w, h = rect(k)
        fill = WHITE if (k in INPUTS or k == "OBJ") else NODE_FILL
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.09", fc=fill, ec=line[t],
                                    lw=2.3 if t == "red" else 1.3, zorder=3))
        label = (NODES.get(k) or INPUTS[k])[0]
        ax.text(x + w / 2, y + h / 2, label, fontsize=11.5 if k in NODES else (9.6 if k == "comp" else 10.5),
                color=text[t], ha="center",
                va="center", zorder=4, linespacing=1.15)
        if ch == 5 and k in LOOKS:
            ax.text(x + w / 2, y + h + 0.08, LOOKS[k], fontsize=9.5, color=RED, ha="center", va="top", zorder=4,
                    linespacing=1.1)
    x0 = (W - (len(CHIPS) * CHIP_W + (len(CHIPS) - 1) * 0.16)) / 2
    ax.text(x0, CHIP_Y - CHIP_H / 2 - 0.08, "The lab's steps (this repository's chapters)", fontsize=9.5, color=GRAY,
            va="bottom")
    for i, (n, name, st) in enumerate(CHIPS):
        if int(n) > ch:
            continue
        t = "red" if n in chips_red else "faint"
        x = x0 + i * (CHIP_W + 0.16)
        ax.add_patch(FancyBboxPatch((x, CHIP_Y - CHIP_H / 2), CHIP_W, CHIP_H, boxstyle="round,pad=0,rounding_size=0.2",
                                    fc=WHITE, ec=line[t], lw=1.8 if t == "red" else 1.1, zorder=3))
        ax.text(x + CHIP_W / 2, CHIP_Y, f"{n}  {name}", fontsize=11, color=RED if t == "red" else LIGHT,
                ha="center", va="center", zorder=4, fontweight="bold" if t == "red" else "normal")
    ax.text(W / 2, CAPTION_Y, caption, fontsize=15, color=INK, ha="center", va="center")
    fig.savefig(path, dpi=DPI, facecolor=WHITE)
    plt.close(fig)


def blend(a: Image.Image, b: Image.Image, u: float) -> Image.Image:
    return Image.blend(a, b, float(np.clip(u, 0, 1)))


def clip(frames_png: list[Path], holds: list[float], path: Path, fps=15, fade=0.8, lead=None):
    """An MP4 of the beats: each held `holds[i]` seconds, cross-faded `fade` s into the next. `lead` is the state
    the clip fades in from (the previous chapter's last beat)."""
    ims = [Image.open(p).convert("RGB") for p in frames_png]
    seq = []
    if lead is not None:
        L = Image.open(lead).convert("RGB")
        seq += [L] * int(0.6 * fps) + [blend(L, ims[0], (i + 1) / int(fade * fps)) for i in range(int(fade * fps))]
    for i, (im, hold) in enumerate(zip(ims, holds)):
        seq += [im] * int(hold * fps)
        if i + 1 < len(ims):
            seq += [blend(im, ims[i + 1], (j + 1) / int(fade * fps)) for j in range(int(fade * fps))]
    with tempfile.TemporaryDirectory() as td:
        for i, im in enumerate(seq):
            im.save(Path(td) / f"f{i:05d}.png")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", str(Path(td) / "f%05d.png"),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", str(path)], check=True)
    return len(seq) / fps


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    record = {"source": SOURCE, "chapters": {}}
    last = None
    finals = []
    for ch, beats in BEATS.items():
        pngs = []
        for i, b in enumerate(beats):
            p = OUT / f"route_dag_ch{ch}_{i}.png"
            draw(ch, b, p)
            pngs.append(p)
        final = OUT / f"route_dag_ch{ch}.png"
        Image.open(pngs[-1]).save(final)
        holds = [3.2] * (len(pngs) - 1) + [5.5]
        secs = clip(pngs, holds, OUT / f"route_dag_ch{ch}.mp4", lead=last)
        for p in pngs:
            if p != final:
                p.unlink()
        record["chapters"][ch] = {"seconds": round(secs, 2), "captions": [b[4] for b in beats],
                                  "mp4": f"out/dag/route_dag_ch{ch}.mp4", "png": f"out/dag/route_dag_ch{ch}.png"}
        last = final
        finals.append(final)
        print(f"chapter {ch}: {secs:.1f} s")
    ims = [Image.open(p).convert("RGB").resize((640, 360), Image.LANCZOS) for p in finals]
    sheet = Image.new("RGB", (640 * 2 + 30, 360 * 3 + 40), "white")
    for i, im in enumerate(ims):
        sheet.paste(im, (10 + (i % 2) * 650, 10 + (i // 2) * 370))
    sheet.save(OUT / "route_dag_sheet.png")
    (OUT / "route_dag.json").write_text(json.dumps(record, indent=1) + "\n")


if __name__ == "__main__":
    main()

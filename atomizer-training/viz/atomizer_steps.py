"""Step-by-step schematic animations of a rePowder ultrasonic atomization run.

A 2-D side section of the machine (induction furnace + graphite crucible + sealing rod + nozzle on top, argon chamber
with the ultrasonic stack and plate in the middle, powder container below, utilities at the right, HMI readouts at the
left) drawn by matplotlib from a dict of state values, interpolated between keyframes and written as GIFs. Each GIF is
one core step of the SOP in ../sop.md. `03_furnace_load_operator.gif` repeats the loading step with a semi-transparent
operator figure doing the motions, as a test of that style (see README).

    python atomizer_steps.py            # renders every step into ./out
    python atomizer_steps.py 06_pour    # one step

Numbers shown in the readouts are the ones used in training (see ../sop.md); they are illustrative, not a recipe.
"""
import io, math, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon, Ellipse, FancyBboxPatch, Wedge, Arc
from PIL import Image

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
FPS = 10
W, H = 8.0, 6.0  # inches at 100 dpi -> 800x600; GIFs are downscaled to 640 px wide

C = dict(steel="#aeb6bf", steel_dark="#7d8791", graphite="#2b2b2b", insul="#e8dcc8", coil="#b87333", coil_hot="#ff9d2e",
         melt="#ff6a00", solid="#9aa3ab", ti="#c8ccd0", plate="#8f9aa5", water="#2a9df4", air="#9e9e9e", argon="#4a7fb5",
         powder="#c9a86a", text="#222222", ok="#2e8b57", warn="#d9534f", op="#1f4e79", glass="#cfe8ff", bg="white")

DEFAULT = dict(
    temp=22.0, p_chamber=0.0, p_furnace=0.0, o2=1000.0, freq=0.0, amp=0.0, coil=0.0, us=0.0,
    rod_lift=0.0, rod_in=1.0, nozzle=1.0, insul=1.0, tc=1.0, lid=0.0, charge=0.0, melt=0.0, stream=0.0, spray=0.0,
    powder=0.0, door=0.0, container=1.0, stack=4.0, water=0.0, air=0.0, argon=0.0, hx=0.0, pump=0.0, vent=0.0,
    turbo=0.0, scan=0.0, wet=0.0, torques=0.0, brush=0.0, bag=0.0, label="", status="", caption="",
    op_vis=0.0, op_x=14.0, op_hand=(14.0, 60.0), op_hold="", op_alpha=0.35,
)


def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * min(max(t, 0.0), 1.0))


def interp(a, b, t):
    out = {}
    for k in b:
        va, vb = a.get(k, DEFAULT[k]), b[k]
        if isinstance(vb, (int, float)) and not isinstance(vb, bool):
            out[k] = va + (vb - va) * ease(t)
        elif isinstance(vb, tuple):
            out[k] = tuple(va[i] + (vb[i] - va[i]) * ease(t) for i in range(len(vb)))
        else:
            out[k] = vb if t >= 0.5 else va
    full = dict(a); full.update(out)
    return full


def frames_for(keys):
    """keys: list of (seconds, partial_state). Cumulative: each target is reached over its segment."""
    state = dict(DEFAULT); out = []
    for secs, target in keys:
        n = max(1, int(round(secs * FPS)))
        goal = dict(state); goal.update(target)
        for i in range(1, n + 1):
            out.append(interp(state, goal, i / n))
        state = goal
    return out


# ----------------------------------------------------------------------------------------------------------------- draw
def readout(ax, x, y, label, value, unit="", color=C["text"], w=17):
    ax.add_patch(FancyBboxPatch((x, y), w, 5.2, boxstyle="round,pad=0.3", fc="#f4f6f8", ec="#c7ccd1", lw=0.8))
    ax.text(x + 0.8, y + 3.4, label, fontsize=6.5, color="#666", va="center")
    ax.text(x + w - 0.8, y + 1.5, f"{value}{unit}", fontsize=8.5, color=color, va="center", ha="right", fontweight="bold")


def valve(ax, x, y, open_, color):
    ax.add_patch(Polygon([[x - 1.6, y - 1.1], [x - 1.6, y + 1.1], [x, y]], fc=color if open_ > 0.5 else "white", ec=color, lw=1))
    ax.add_patch(Polygon([[x + 1.6, y - 1.1], [x + 1.6, y + 1.1], [x, y]], fc=color if open_ > 0.5 else "white", ec=color, lw=1))
    ax.plot([x, x], [y, y + 2.2], color=color, lw=1)
    ax.plot([x - 1.2, x + 1.2], [y + 2.2, y + 2.2], color=color, lw=1.6)


def operator(ax, s, frame_idx):
    """Semi-transparent human figure; the hand position is animated and may carry a part."""
    if s["op_vis"] <= 0.01:
        return
    a = s["op_alpha"] * s["op_vis"]; x = s["op_x"]; col = C["op"]
    hx, hy = s["op_hand"]
    # body
    ax.add_patch(Circle((x, 48), 3.2, fc=col, ec="none", alpha=a))
    ax.plot([x, x], [44.5, 30], color=col, lw=7, alpha=a, solid_capstyle="round")
    ax.plot([x, x - 3.5], [30, 12], color=col, lw=5, alpha=a, solid_capstyle="round")
    ax.plot([x, x + 3.5], [30, 12], color=col, lw=5, alpha=a, solid_capstyle="round")
    # arm: shoulder -> elbow -> hand (two-link IK, elbow bent downward-forward)
    sx, sy = x + 1.5, 42.0
    L1 = L2 = 11.0
    dx, dy = hx - sx, hy - sy
    d = max(1e-6, min(math.hypot(dx, dy), L1 + L2 - 0.5))
    ang = math.atan2(dy, dx)
    cos_a = (L1 ** 2 + d ** 2 - L2 ** 2) / (2 * L1 * d)
    cos_a = max(-1.0, min(1.0, cos_a))
    a1 = ang - math.acos(cos_a) * (1 if hx > sx else -1)
    ex, ey = sx + L1 * math.cos(a1), sy + L1 * math.sin(a1)
    ax.plot([sx, ex, hx], [sy, ey, hy], color=col, lw=5, alpha=a, solid_capstyle="round", solid_joinstyle="round")
    ax.add_patch(Circle((hx, hy), 1.6, fc=col, ec="none", alpha=a))
    # the other arm hangs
    ax.plot([x - 1.5, x - 4], [42, 30], color=col, lw=5, alpha=a, solid_capstyle="round")
    # carried part
    if s["op_hold"] == "charge":
        ax.add_patch(Rectangle((hx - 1.1, hy - 6.5), 2.2, 6.5, fc=C["solid"], ec="#555", lw=0.8))
    elif s["op_hold"] == "rod":
        ax.plot([hx, hx], [hy - 9, hy + 2], color=C["graphite"], lw=2.2)
        ax.add_patch(Circle((hx, hy - 9), 0.9, fc=C["graphite"], ec="none"))
    elif s["op_hold"] == "brush":
        ax.plot([hx, hx + 4], [hy, hy - 3], color="#8b5a2b", lw=2.5)
        ax.add_patch(Rectangle((hx + 3.5, hy - 4.5), 2.4, 1.8, fc="#d4a76a", ec="none"))


def draw(s, frame_idx):
    fig = plt.figure(figsize=(W, H), dpi=100); ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    rng = np.random.default_rng(frame_idx)
    temp, coil = s["temp"], s["coil"]
    # ---------------------------------------------------------------- utilities (right)
    # argon cylinder + regulator
    ax.add_patch(FancyBboxPatch((87, 8), 5, 26, boxstyle="round,pad=0.3", fc=C["argon"], ec="#2d5a8a", lw=1))
    ax.text(89.5, 21, "Ar\n5N", ha="center", va="center", fontsize=7, color="white", fontweight="bold")
    valve(ax, 89.5, 37.5, s["argon"], C["argon"])
    ax.text(89.5, 42.5, f"{8 * s['argon']:.0f} bar", ha="center", fontsize=6.5, color=C["argon"])
    # argon lines to furnace and chamber
    lw_ar = 1 + 1.2 * s["argon"]
    ax.plot([89.5, 89.5, 66], [40, 80, 80], color=C["argon"], lw=lw_ar, alpha=0.4 + 0.6 * s["argon"])
    ax.plot([89.5, 81], [55, 55], color=C["argon"], lw=lw_ar, alpha=0.4 + 0.6 * s["argon"])
    # compressed air to transducer
    ax.text(93, 3.5, "air", fontsize=6.5, color=C["air"], ha="center")
    valve(ax, 93, 6.5, s["air"], C["air"])
    ax.plot([93, 93, 56], [9, 14, 14], color=C["air"], lw=1 + 1.2 * s["air"], alpha=0.4 + 0.6 * s["air"], ls="-")
    # vacuum pump
    ax.add_patch(Rectangle((70, 2), 12, 6, fc="#d9dde2", ec=C["steel_dark"], lw=1))
    ax.text(76, 5, "vacuum\npump", ha="center", va="center", fontsize=6)
    if s["pump"] > 0.5:
        ax.add_patch(Circle((80.5, 7.3), 0.9, fc=C["ok"], ec="none"))
    ax.plot([76, 76, 80], [8, 20, 20], color=C["steel_dark"], lw=1.2, ls="--" if s["pump"] < 0.5 else "-")
    # heat exchanger + chilled water
    ax.add_patch(Rectangle((2, 2), 11, 8, fc="#e3eef9", ec=C["water"], lw=1))
    ax.text(7.5, 6, "heat\nexchanger", ha="center", va="center", fontsize=6, color="#1b5e97")
    if s["hx"] > 0.5:
        ax.add_patch(Circle((12, 9.2), 0.9, fc=C["ok"], ec="none"))
    valve(ax, 7.5, 13.5, s["water"], C["water"])
    ax.text(7.5, 16.3, "facility\nchilled water", ha="center", fontsize=5.5, color="#1b5e97")
    lw_w = 1 + 1.4 * s["water"]
    ax.plot([4, 4, 20], [10, 24, 24], color=C["water"], lw=lw_w, alpha=0.35 + 0.65 * s["water"])
    ax.plot([11, 18.5, 18.5, 35, 35], [10, 10, 55, 55, 60], color=C["water"], lw=lw_w, alpha=0.35 + 0.65 * s["water"])
    # ---------------------------------------------------------------- chamber
    door = s["door"]
    ax.add_patch(Rectangle((20, 20), 60, 40, fc="#eef1f4", ec=C["steel_dark"], lw=2))
    ax.add_patch(Rectangle((20, 20), 60, 40, fill=False, ec=C["steel"], lw=6, alpha=0.5))
    ax.text(21.5, 57.3, "argon chamber", fontsize=7, color="#555")
    # view port
    ax.add_patch(Circle((27, 46), 4.2, fc=C["glass"], ec=C["steel_dark"], lw=1.2))
    ax.text(27, 40.2, "view port", ha="center", fontsize=5.5, color="#555")
    # door (drawn as a panel swinging out to the right when open)
    if door > 0.02:
        ang = 80 * door
        ax.add_patch(Polygon([[80, 20], [80 + 24 * math.sin(math.radians(ang)) * 0.9, 20 + 6 * door], [80 + 24 * math.sin(math.radians(ang)) * 0.9, 60 - 6 * door], [80, 60]],
                             fc="#dfe4e8", ec=C["steel_dark"], lw=1.5, alpha=0.9))
        ax.text(81, 62, "door open", fontsize=6, color=C["warn"])
    else:
        for yy in (25, 39, 53):  # three clamps
            ax.add_patch(Rectangle((79, yy), 2.6, 3, fc=C["steel_dark"], ec="none"))
    # cone and container
    ax.add_patch(Polygon([[36, 20], [64, 20], [56, 13], [44, 13]], fc="#e3e7eb", ec=C["steel_dark"], lw=1.2))
    cx = 50 + 18 * (1 - s["container"])  # slides out to the right when detached
    ax.add_patch(Rectangle((cx - 6, 2), 12, 11, fc="#dfe4e8", ec=C["steel_dark"], lw=1.5))
    ax.text(cx + 6.6, 7.5, "powder\ncontainer", fontsize=5.5, color="#555", va="center")
    if s["powder"] > 0:
        ax.add_patch(Rectangle((cx - 5.6, 2.4), 11.2, 10 * s["powder"], fc=C["powder"], ec="none"))
    valve(ax, cx, 14.2, 1 - (s["container"] < 0.5), C["steel_dark"])
    # ---------------------------------------------------------------- ultrasonic stack
    st = s["stack"]
    if st >= 1:
        ax.add_patch(Rectangle((46, 6), 8, 10, fc="#b9c0c7", ec=C["steel_dark"], lw=1)); ax.text(50, 11, "transducer", ha="center", va="center", fontsize=5.5)
        ax.text(57.5, 9, "65 N·m", fontsize=5.5, color="#555") if (st >= 2 and s["torques"] > 0.5) else None
    if st >= 2:
        ax.add_patch(Rectangle((47, 16), 6, 9, fc=C["ti"], ec=C["steel_dark"], lw=1)); ax.text(50, 20.5, "booster\n1.5:1", ha="center", va="center", fontsize=5)
        ax.text(57.5, 24, "60 N·m", fontsize=5.5, color="#555") if (st >= 3 and s["torques"] > 0.5) else None
    if st >= 3:
        ax.add_patch(Polygon([[47, 25], [53, 25], [51.5, 42], [48.5, 42]], fc=C["ti"], ec=C["steel_dark"], lw=1)); ax.text(50, 33, "sonotrode", ha="center", va="center", fontsize=5, rotation=90)
        ax.text(57.5, 41, "50 N·m", fontsize=5.5, color="#555") if (st >= 4 and s["torques"] > 0.5) else None
    if st >= 4:
        ax.add_patch(Polygon([[43, 43.2], [57, 45.2], [57, 46.4], [43, 44.4]], fc=C["plate"], ec="#444", lw=1))  # tilted plate
        ax.text(60, 46.5, "plate (Mo)", fontsize=5.5, color="#555")
        if s["us"] > 0.05:  # vibration lines
            for k in range(3):
                ax.plot([41 - k * 1.3, 41 - k * 1.3], [43 - k, 47 + k], color="#333", lw=0.8, alpha=0.7 * s["us"])
                ax.plot([59 + k * 1.3, 59 + k * 1.3], [43 - k, 47 + k], color="#333", lw=0.8, alpha=0.7 * s["us"])
        if s["wet"] > 0.05:
            ax.add_patch(Ellipse((50, 45.2), 9 * s["wet"], 1.4, fc=C["water"], ec="none", alpha=0.7))
    # ---------------------------------------------------------------- furnace
    ax.add_patch(Rectangle((33, 60), 34, 29, fc="#d6dadf", ec=C["steel_dark"], lw=2))
    ax.text(34.5, 86.8, "induction furnace", fontsize=7, color="#555")
    if s["insul"] > 0.5:
        ax.add_patch(Rectangle((37, 62), 26, 24, fc=C["insul"], ec="#cdbfa6", lw=1))
    # coil rings
    for i, yy in enumerate(np.linspace(66, 82, 6)):
        colc = C["coil_hot"] if coil > 0.5 else C["coil"]
        ax.add_patch(Ellipse((50, yy), 20, 2.6, fill=False, ec=colc, lw=2.2 + 1.2 * coil, alpha=0.95))
    if coil > 0.05:
        ax.add_patch(Rectangle((42, 64), 16, 21, fc=C["coil_hot"], ec="none", alpha=0.18 * coil))
    # crucible (U) + nozzle holder
    ax.add_patch(Polygon([[42, 87], [42, 66], [45, 63], [55, 63], [58, 66], [58, 87], [56.5, 87], [56.5, 67], [54.5, 65], [45.5, 65], [43.5, 67], [43.5, 87]],
                         fc=C["graphite"], ec="none"))
    ax.text(59.5, 84, "graphite\ncrucible", fontsize=5.5, color="#555")
    if s["nozzle"] > 0.5:
        ax.add_patch(Rectangle((47.5, 63.2), 5, 1.8, fc="#4a4a4a", ec="none"))
        ax.add_patch(Rectangle((49.6, 62.8), 0.8, 2.6, fc="white", ec="none"))  # the bore
        ax.text(59.5, 63.5, "nozzle Ø0.7", fontsize=5.5, color="#555")
    # charge / melt
    ch, ml = s["charge"], s["melt"]
    if ch > 0.01:
        solid_h = 20 * ch * (1 - ml)
        liq_h = 9 * ch * ml
        if liq_h > 0.05:
            ax.add_patch(Rectangle((45.5, 65), 9, liq_h, fc=C["melt"], ec="none", alpha=0.95))
        if solid_h > 0.05:
            ax.add_patch(Rectangle((48, 65 + liq_h), 4, solid_h, fc=C["solid"], ec="#666", lw=0.6))
    # sealing rod
    if s["rod_in"] > 0.5:
        lift = 8 * s["rod_lift"]
        ax.plot([50, 50], [65.2 + lift, 92.5], color=C["graphite"], lw=2.4)
        ax.add_patch(Circle((50, 65.3 + lift), 1.0, fc=C["graphite"], ec="none"))
        ax.text(52, 90.3, "sealing rod", fontsize=5.5, color="#555")
    # thermocouple
    if s["tc"] > 0.5:
        ax.plot([67, 60, 59], [72, 72, 72], color="#444", lw=1.5); ax.text(68, 71, "TC", fontsize=5.5, color="#555")
    # lid
    lid = s["lid"]
    if lid < 0.02:
        ax.add_patch(Rectangle((33, 89.2), 34, 2.2, fc=C["steel_dark"], ec="none"))
    else:
        ang = math.radians(70 * lid)
        ax.add_patch(Polygon([[67, 89.5], [67 - 34 * math.cos(ang), 89.5 + 34 * math.sin(ang)], [67 - 34 * math.cos(ang), 91.7 + 34 * math.sin(ang)], [67, 91.7]], fc=C["steel_dark"], ec="none"))
    # stream, spray, falling powder
    if s["stream"] > 0.02:
        ax.plot([50, 50], [62.5, 46], color=C["melt"], lw=1.2 + 1.6 * s["stream"], alpha=0.95)
        ax.add_patch(Circle((50, 46), 1.1 * s["stream"], fc=C["melt"], ec="none"))
    if s["spray"] > 0.02:
        n = int(60 * s["spray"])
        ang = rng.uniform(0.15, math.pi - 0.15, n); r = rng.uniform(2, 16, n)
        px = 50 + r * np.cos(ang); py = 45 + r * np.sin(ang) * 0.6 - r ** 1.3 * 0.25
        ax.scatter(px, py, s=10 * s["spray"], c=[C["melt"]], alpha=0.8, edgecolors="none")
        fy = rng.uniform(20, 40, n // 2); fx = rng.uniform(38, 62, n // 2)
        ax.scatter(fx, fy, s=6, c=[C["powder"]], alpha=0.8, edgecolors="none")
    if s["turbo"] > 0.3:
        ax.text(50, 55, "TURBO", ha="center", fontsize=8, color=C["warn"], fontweight="bold", alpha=s["turbo"])
    if s["vent"] > 0.3:
        ax.annotate("", xy=(84, 56), xytext=(80, 56), arrowprops=dict(arrowstyle="->", color=C["argon"], lw=2))
        ax.text(84.5, 55, "vent", fontsize=6, color=C["argon"], va="center")
    if s["brush"] > 0.02:
        bx = 44 + 12 * (0.5 + 0.5 * math.sin(frame_idx * 0.9))
        ax.plot([bx - 3, bx + 3], [27, 25], color="#8b5a2b", lw=2.5, alpha=0.9)
        ax.add_patch(Rectangle((bx + 2.5, 22.5), 2.4, 2, fc="#d4a76a", ec="none"))
    if s["bag"] > 0.02:
        ax.add_patch(FancyBboxPatch((70, 4), 9, 10 * s["bag"] + 0.1, boxstyle="round,pad=0.2", fc="#f5f0e6", ec="#999", lw=1, alpha=min(1, s["bag"] * 2)))
        ax.add_patch(Rectangle((71, 6), 7, 4 * s["bag"], fc=C["powder"], ec="none", alpha=min(1, s["bag"] * 2)))
        ax.text(74.5, 12, "u23y78", ha="center", fontsize=6, fontweight="bold", alpha=min(1, s["bag"] * 2))
    # scan inset
    if s["scan"] > 0.02:
        ax.add_patch(FancyBboxPatch((63, 24), 15, 10, boxstyle="round,pad=0.3", fc="white", ec="#aaa", lw=0.8, alpha=0.95))
        f = np.linspace(39, 41, 120); peak = np.exp(-((f - 40.12) / 0.12) ** 2)
        ax.plot(63.5 + (f - 39) / 2 * 14, 25 + 7 * peak * s["scan"], color=C["ok"], lw=1.3)
        ax.text(70.5, 32.6, "scan 39–41 kHz: one peak", ha="center", fontsize=5, color="#555")
    # ---------------------------------------------------------------- readouts (left)
    tcol = C["warn"] if temp > 600 else (C["text"] if temp > 60 else "#1b5e97")
    readout(ax, 2, 85, "furnace temperature", f"{temp:.0f}", " °C", tcol)
    readout(ax, 2, 78.5, "furnace pressure", f"{s['p_furnace']:+.0f}", " mbar")
    readout(ax, 2, 72, "chamber pressure", f"{s['p_chamber']:+.0f}", " mbar")
    ocol = C["ok"] if s["o2"] <= 100 else C["warn"]
    readout(ax, 2, 65.5, "oxygen", f"{s['o2']:.0f}", " ppm", ocol)
    readout(ax, 2, 59, "ultrasonic", f"{s['freq']:.2f} kHz · {s['amp']:.0f}" if s["freq"] else "off", " %" if s["freq"] else "", C["ok"] if s["us"] > 0.5 else C["text"])
    if s["status"]:
        ax.text(2, 57.2, s["status"], fontsize=6.5, color=C["warn"] if "!" in s["status"] else "#444", va="top", wrap=True)
    # ---------------------------------------------------------------- operator, title, caption
    operator(ax, s, frame_idx)
    ax.text(50, 99.4, s["label"], ha="center", va="top", fontsize=10.5, fontweight="bold", color=C["text"])
    if s["caption"]:
        ax.add_patch(Rectangle((0, 0), 100, 0.1, fc="none", ec="none"))
        ax.text(50, 95.9, s["caption"], ha="center", va="top", fontsize=7.5, color="#333",
                bbox=dict(boxstyle="round,pad=0.35", fc="#fff8e6", ec="#e0c98c", lw=0.8))
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=100); plt.close(fig); buf.seek(0)
    im = Image.open(buf).convert("RGB"); im.thumbnail((640, 480))
    return im


# ------------------------------------------------------------------------------------------------------------ steps
READY = dict(water=1, air=1, argon=1, hx=1)  # utilities on


def step_01_utilities():
    L = "1 · Utilities on (before heating)"
    return [
        (1.0, dict(label=L, caption="Breakers on. Everything else is still off.", temp=22, o2=1000, stack=4)),
        (1.2, dict(water=1, caption="Facility chilled water: open the valve only a little (≥2 L/min, but 'water too cold' trips below 7–10 °C)")),
        (1.0, dict(hx=1, caption="Heat exchanger on only when you are about to heat; wait for 'cooling water flow low' to clear")),
        (1.2, dict(air=1, caption="Compressed air: 8 bar supply, ~4 bar regulated. It only cools the transducer; no air = no ultrasonics")),
        (1.2, dict(argon=1, caption="Argon 5N at 8 bar on the regulator, one T into the furnace line and the chamber line")),
        (1.5, dict(caption="Checklist: pump oil in the sight glass, exchanger water level, HEPA (every ~2 months), hoses dry")),
    ]


def step_02_stack():
    L = "2 · Ultrasonic stack: build, torque, scan"
    return [
        (0.8, dict(label=L, **READY, stack=0, torques=1, caption="Stack goes transducer → booster → sonotrode → plate. Never drop or wet the transducer")),
        (1.0, dict(stack=1, caption="Transducer (piezo stack, ~1000 V cable, air cooled). Hold it while anything is loose")),
        (1.0, dict(stack=2, caption="Booster, torque 65 N·m at the transducer (M10 fine). 1.5:1 reversed = lower amplitude = finer powder")),
        (1.0, dict(stack=3, caption="Sonotrode, torque 60 N·m. KF50 flange is always the top; IPA on the threads")),
        (1.0, dict(stack=4, caption="Plate on its M8 connector stud, torque 50 N·m with the stack in the housing; counter-hold with a 17 mm wrench")),
        (1.3, dict(scan=1, freq=40.12, caption="Advanced ultrasonics → scan: one wide peak a little over 40 kHz. Double peak? short burst, rescan")),
        (1.3, dict(us=1, amp=90, wet=1, caption="Wet test: a drop of water should atomize over the whole plate. Half the plate = a crack")),
        (0.8, dict(us=0, wet=0, scan=0, freq=0, amp=0, caption="Bolt the protective cover over the transducer (2–3 min that saves a part worth thousands)")),
    ]


def step_03_furnace_load(with_operator=False):
    L = "3 · Furnace prep and loading"
    op = dict(op_vis=1.0) if with_operator else {}
    keys = [
        (0.8, dict(label=L, **READY, **op, stack=4, lid=1, rod_in=0, nozzle=0, insul=0, tc=0, charge=0, op_hand=(14, 62), caption="Furnace open and cool. Everything out: thermocouple, sealing rod, insulation, crucible nut")),
        (1.2, dict(nozzle=1, op_hand=(44, 70) if with_operator else (14, 62), caption="Nozzle (Ø0.5 standard; Ø0.7 for Al alloys) into the crucible first, white side up; thread the crucible on until just tight")),
        (1.2, dict(rod_in=1, rod_lift=0.9, op_hold="rod" if with_operator else "", op_hand=(50, 85) if with_operator else (14, 62), caption="Sealing rod in before any metal, tip clean and undamaged (a damaged tip will not seal)")),
        (0.8, dict(rod_lift=0, op_hold="", caption="Seat the rod on the nozzle; align the nut's hole where you can reach it before tightening fully")),
        (1.0, dict(insul=1, tc=1, op_hand=(40, 78) if with_operator else (14, 62), caption="Side + top insulation (silica/alumina, dusty: vacuum), thermocouple hole aligned and bent in close")),
        (1.2, dict(op_hold="charge" if with_operator else "", op_hand=(49, 92) if with_operator else (14, 62), charge=0.0, caption="Charge: clean feedstock, ≤20 mm diameter, 250–300 g recommended; powder only inside a vented Al cup")),
        (1.0, dict(charge=1.0, op_hold="", op_hand=(49, 92) if with_operator else (14, 62), caption="Rods stand proud and sink as they melt. BN-spray the crucible the night before for reactive alloys")),
        (1.0, dict(lid=0, op_hand=(40, 96) if with_operator else (14, 62), caption="Close the lid just tight enough to seal: if it hisses under pressure, re-adjust the latch")),
        (0.8, dict(op_hand=(14, 62), caption="Container clamped (two people), splash plate above it, catch bowl in, covers hung, three door clamps")),
    ]
    return keys


def step_04_gas_wash():
    L = "4 · Gas wash: vacuum ↔ argon, furnace then chamber"
    keys = [(0.8, dict(label=L, **READY, charge=1, pump=1, caption="Pressure control OFF before pumping. Keep overpressure in the vessel you are not washing"))]
    for i in range(3):
        keys.append((0.5, dict(p_furnace=-850, p_chamber=150, o2=max(45, 1000 - 300 * (i + 1)), status=f"furnace gas wash {i + 1}/5", caption="Gauge floor is about −850 mbar at Provo altitude (−1000 at sea level): normal, not a leak")))
        keys.append((0.5, dict(p_furnace=+150)))
    keys.append((0.5, dict(p_furnace=+150, p_chamber=-850, status="chamber wash", caption="Then the chamber: pump to the floor, fill with argon, repeat. O2 reads nonsense under vacuum")))
    keys.append((0.5, dict(p_chamber=+150, o2=120)))
    keys.append((1.2, dict(coil=1, temp=250, status="250 °C · wash again", caption="Generator start, 250 °C, wash again: the target is moisture in insulation and crucible, not the metal")))
    keys.append((0.5, dict(p_furnace=-850)))
    keys.append((0.5, dict(p_furnace=150, o2=60)))
    keys.append((1.2, dict(temp=500, status="500 °C · wash again", caption="500 °C, wash again. Stop washing when O2 is stable and low: ≤100 ppm, best 40–50 (team saw low 20s)")))
    keys.append((0.5, dict(p_furnace=-850)))
    keys.append((0.8, dict(p_furnace=130, o2=45, status="O2 45 ppm ✓ pressure control ON (150 mbar)", caption="Melting pressure: furnace slightly below chamber. Pressure control back on. Ready to melt")))
    return keys


def step_05_melt():
    L = "5 · Melt: overshoot to drop the rods, hold at ~800 °C, wait 2 min"
    return [
        (0.8, dict(label=L, **READY, charge=1, pump=1, coil=1, temp=500, p_furnace=130, p_chamber=150, o2=45, caption="Setpoint 850–1000 °C: long rods heat at the bottom and cool at the top, so overshoot first")),
        (1.8, dict(temp=1000, status="heating", caption="Watch for the melt cues: a small temperature dip as melt touches the thermocouple, faster induction beeping")),
        (1.8, dict(melt=1.0, temp=870, status="rods slumping → lower setpoint", caption="As soon as the charge slumps, bring the setpoint down to 780–800 °C (plate durability)")),
        (1.5, dict(temp=795, status="800 °C · wait 2 min (no longer)", caption="2 min after everything is liquid: the crucible-wall thermocouple lags the melt. Longer only oxidizes it")),
        (1.0, dict(caption="Meanwhile: transducer cooling on, rescan (scans expire), hearing protection on, operator at the window")),
    ]


def step_06_pour():
    L = "6 · Pour and atomize"
    return [
        (0.8, dict(label=L, **READY, charge=1, melt=1, pump=1, coil=1, temp=795, p_furnace=130, p_chamber=150, o2=45, caption="Order, quickly: vibration ON → draining pressure → sealing rod UP → turbo as needed")),
        (0.8, dict(us=1, freq=40.08, amp=90, status="amplitude 90 % (80–90 best)", caption="Amplitude is % of generator current. Start ~90 and adjust; lower = finer but may not atomize")),
        (0.8, dict(p_furnace=220, status="draining pressure", caption="Draining (pouring) pressure above chamber pressure pushes the melt out; only the differential matters")),
        (0.8, dict(rod_lift=1, stream=1, status="sealing rod up", caption="Melt stream onto the plate. The first droplet usually bounces: a dry plate does not wet")),
        (0.8, dict(turbo=1, stream=1.3, p_furnace=1500, caption="Short TURBO push (1.5 bar) heats the plate and clears debris; pouring MORE at the start is what makes it wet")),
        (1.8, dict(turbo=0, p_furnace=220, spray=1, stream=1, charge=0.6, powder=0.3, status="atomizing", caption="Once the plate is hot every drop atomizes. Steer with plate position: land high, not over the top")),
        (1.6, dict(spray=1, charge=0.3, powder=0.6, caption="Too thin a stream gathers and drips; melt shooting past the plate = pressure too high (Oct 2 lesson)")),
        (1.2, dict(spray=0.8, charge=0.05, powder=0.8, caption="2–3 minutes of attention: amplitude slider, turbo pulses, plate position")),
    ]


def step_07_end_cooldown():
    L = "7 · End of pour, cooldown, open, collect"
    return [
        (0.8, dict(label=L, **READY, charge=0.05, melt=1, pump=1, coil=1, temp=795, p_furnace=220, p_chamber=150, o2=60, us=1, freq=40.08, amp=90, rod_lift=1, stream=0.5, spray=0.5, powder=0.8, caption="Crucible empty: one turbo push to clear the nozzle")),
        (0.6, dict(turbo=1, p_furnace=1500, stream=0.3, spray=0.3)),
        (0.6, dict(turbo=0, rod_lift=0, stream=0, spray=0, p_furnace=130, status="rod down · melting pressure", caption="Sealing rod down, melting pressure, generator STOP, ultrasonics STOP, all within seconds")),
        (0.6, dict(coil=0, us=0, freq=0, amp=0, charge=0, status="generator stop · ultrasonics stop", caption="Vibrating against solidified metal cracks the plate. Set 250 °C for next time; transducer cooling off")),
        (1.8, dict(temp=400, status="cooling… open at ≤400 °C", caption="Open at or below 400 °C: above 500 °C graphite burns in air. Cooling water stays on until ~100 °C")),
        (0.8, dict(vent=1, p_chamber=0, pump=0, status="pressure control off · VENT", caption="Pressure control off, press vent. The door locks while pressure is off-atmospheric. Masks and coat on")),
        (1.0, dict(door=1, vent=0, caption="Three clamps, door open. Chamber and cone are water-cooled and wet; the furnace parts are still hot")),
        (1.2, dict(brush=1, powder=0.95, caption="Brush plate, bowl, walls and view port down into the container; paper under the opening")),
        (1.0, dict(brush=0, container=0.0, caption="Close the container valve first (it is heavier than it looks), then take it off. Argon stays in it")),
        (1.2, dict(bag=1, powder=0.95, caption="Pour onto paper, pick out chunks, sieve, bag it, 6-character ID label, photo on GitHub (#249)")),
        (0.8, dict(temp=100, status="~100 °C: shut down utilities", caption="Heat exchanger, water, air, argon, power: any order at ~100 °C. The program lets you leave at 80 °C")),
    ]


def step_08_clean():
    L = "8 · Clean and reset"
    return [
        (0.8, dict(label=L, water=0, air=0, argon=0, hx=0, temp=60, door=1, container=0, powder=0, caption="Same alloy next: open, brush, vacuum. Material change: ~1 h, vacuum then wipe everything")),
        (1.4, dict(brush=1, caption="Brushes, paper towels and isopropanol only. Stainless scraper for stuck particles; never plastic")),
        (1.0, dict(brush=0, stack=3, caption="Plate off: never grind or clean it; dedicate one plate per alloy and log it (1–3 runs each)")),
        (1.0, dict(lid=1, rod_lift=0.9, caption="Furnace cool: rod out, peel slag from the crucible floor, scrape Al off the rod shaft, keep the tip smooth")),
        (1.0, dict(nozzle=0, caption="Nozzle: look through it for light. Unclog with a needle or drill to Ø0.7; swap if a new charge would not push through")),
        (1.0, dict(nozzle=1, rod_lift=0, lid=0, door=0, container=1, stack=4, caption="Reassemble: nozzle, crucible, rod, insulation, thermocouple; O-rings wiped; HEPA every ~2 months (sand tray)")),
    ]


STEPS = {
    "01_utilities": step_01_utilities, "02_stack": step_02_stack, "03_furnace_load": step_03_furnace_load,
    "03_furnace_load_operator": lambda: step_03_furnace_load(True), "04_gas_wash": step_04_gas_wash,
    "05_melt": step_05_melt, "06_pour": step_06_pour, "07_end_cooldown": step_07_end_cooldown, "08_clean": step_08_clean,
}


def render(name, hold_last=1.2):
    frames = frames_for(STEPS[name]())
    ims = [draw(s, i) for i, s in enumerate(frames)]
    ims += [ims[-1]] * int(hold_last * FPS)
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"{name}.gif")
    pal = [im.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for im in ims]
    pal[0].save(path, save_all=True, append_images=pal[1:], duration=int(1000 / FPS), loop=0, optimize=True)
    ims[len(ims) // 2].save(os.path.join(OUT, f"{name}_still.png"))
    print(name, len(ims), "frames", f"{os.path.getsize(path) / 1e6:.2f} MB", flush=True)


if __name__ == "__main__":
    for n in (sys.argv[1:] or list(STEPS)):
        render(n)

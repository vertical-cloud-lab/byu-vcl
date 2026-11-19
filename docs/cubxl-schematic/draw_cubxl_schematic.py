"""Draw the annotated CubXL schematic for the ONR YIP Equipment attachment (#307).

    python docs/cubxl-schematic/draw_cubxl_schematic.py

writes cubxl_schematic.pdf (vector, fonts embedded) and cubxl_schematic.png
(300 dpi) next to this file, 6.5 in x 3.2 in, Times New Roman throughout.

The machine is a simplified line model in an orthographic axonometric view,
in mm (x to the right, y away from the viewer, z up, deck surface at z = 0).
The head and the labware are placed from the calibration every run since
2026-10-02 has used (copies on main in
cubos/results/pipette_test_20261007/configs/):

  * cub_xl_ben_3_instrument.yaml: capper at offset (0, 0), the P20 pipette
    at (+55.0, +11.0), the head camera mount at (-40.0, +10.0)
  * ben_2vials_tiprack.yaml: vials (28 mm) at x 136.668, 33 mm apart in y;
    the 2 x 15 tip rack with A1 at x 291.332, A2 one 8.5 mm step in -x,
    rows every 8.5 mm in +y

The layout in y, the 9-cup vial column with six vials loaded, and the
controller box and potentiostat to the right of the machine follow the
overhead deck-camera still of 2026-10-22 (byu-vcl PR #291). The frame
members (extrusions, gantry plates, motors, end plates) are stand-ins for the
Genmitsu PROVerXL 4030 V2 parts, sized to look right rather than measured.

Callouts come in two styles, set per row of CALLOUTS:
  solid black leader + black label   implemented and tested on the CubXL
  dashed grey leader + grey label    planned: the part is a dashed grey ghost
The evidence for every callout is the table in README.md.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Polygon  # noqa: E402

HERE = Path(__file__).resolve().parent
FIG_W_IN, FIG_H_IN = 6.5, 3.2

plt.rcParams.update(
    {
        "font.family": "Times New Roman",
        "mathtext.fontset": "custom",
        "mathtext.rm": "Times New Roman",
        "pdf.fonttype": 42,  # embed TrueType, keep text selectable
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    }
)

INK = "#1a1a1a"
PLANNED = "#8c8c8c"
GHOST_FILL = (1, 1, 1, 0.55)  # planned parts: a faint veil, dashed edges
LW = 0.55  # model edge width, pt

# ---------------------------------------------------------------------------
# projection
# ---------------------------------------------------------------------------
AZ = np.radians(28.0)  # view from the front-right
EL = np.radians(24.0)  # and from above
RIGHT = np.array([np.cos(AZ), np.sin(AZ), 0.0])
TO_CAM = np.array([np.sin(AZ) * np.cos(EL), -np.cos(AZ) * np.cos(EL), np.sin(EL)])
UP = np.cross(TO_CAM, RIGHT)


def proj(p):
    """World (x, y, z) mm -> screen (u, v) mm and depth (larger = further)."""
    p = np.asarray(p, dtype=float)
    return p @ RIGHT, p @ UP, -(p @ TO_CAM)


def uv(p):
    u, v, _ = proj(p)
    return np.array([u, v])


def shade(rgb, factor):
    rgb = np.array(matplotlib.colors.to_rgb(rgb))
    return tuple(np.clip(rgb * factor, 0, 1))


# ---------------------------------------------------------------------------
# scene: a list of primitives, painted back to front
# ---------------------------------------------------------------------------
class Scene:
    """Painter's algorithm in two levels.

    Layers paint in increasing order.  Inside a layer, parts paint in the
    order they were added, except in `DEPTH_SORTED` layers, which sort by
    centroid depth.  Centroid sorting is wrong for parts stacked at different
    heights (a low part far back can be nearer the camera than a tall one in
    front), so the head and the labware are ordered by hand instead.
    """

    DEPTH_SORTED = set()

    def __init__(self):
        self.items = []  # (layer, seq, depth, draw_fn)

    def add(self, depth, fn, layer=1):
        self.items.append((layer, len(self.items), depth, fn))

    def draw(self, ax):
        def key(t):
            layer, seq, depth, _ = t
            return (layer, -depth if layer in self.DEPTH_SORTED else seq)

        for *_, fn in sorted(self.items, key=key):
            fn(ax)

    # -- primitives -------------------------------------------------------
    def box(self, x0, x1, y0, y1, z0, z1, color="#d9d9d9", layer=1, lw=LW,
            ghost=False, depth_bias=0.0):
        """Axis-aligned box; only the faces that look at the camera."""
        c = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
                      [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]])
        faces = [  # (vertex indices, outward normal, shade factor)
            ([4, 5, 6, 7], (0, 0, 1), 1.00),
            ([0, 3, 2, 1], (0, 0, -1), 0.70),
            ([0, 1, 5, 4], (0, -1, 0), 0.90),
            ([2, 3, 7, 6], (0, 1, 0), 0.80),
            ([1, 2, 6, 5], (1, 0, 0), 0.80),
            ([3, 0, 4, 7], (-1, 0, 0), 0.86),
        ]
        center = c.mean(axis=0)
        depth = proj(center)[2] + depth_bias
        polys = []
        for idx, n, f in faces:
            if np.dot(n, TO_CAM) <= 1e-9:
                continue
            pts = np.array([uv(c[i]) for i in idx])
            polys.append((pts, shade(color, f)))

        def fn(ax, polys=polys):
            for pts, fc in polys:
                if ghost:
                    ax.add_patch(Polygon(pts, closed=True, fc=GHOST_FILL, ec=PLANNED,
                                         lw=lw, ls=(0, (2.2, 1.4)), joinstyle="round",
                                         zorder=1))
                else:
                    ax.add_patch(Polygon(pts, closed=True, fc=fc, ec=INK, lw=lw,
                                         joinstyle="round", zorder=1))

        self.add(depth, fn, layer)
        return center

    def cylinder(self, cx, cy, z0, z1, r, color="#e6e6e6", top=None, layer=1,
                 lw=LW, ghost=False, depth_bias=0.0, n=72):
        """Vertical cylinder: side silhouette plus the top ellipse."""
        t = np.linspace(0, 2 * np.pi, n, endpoint=False)
        ring = np.stack([cx + r * np.cos(t), cy + r * np.sin(t)], axis=1)
        bot = np.array([uv((x, y, z0)) for x, y in ring])
        topr = np.array([uv((x, y, z1)) for x, y in ring])
        # the silhouette: tangent points sit at +/- RIGHT from the axis
        th0 = np.arctan2(RIGHT[1], RIGHT[0])
        s = np.linspace(th0, th0 + np.pi, n // 2 + 1)  # back half (top arc)
        f = np.linspace(th0 + np.pi, th0 + 2 * np.pi, n // 2 + 1)  # front half
        top_back = np.array([uv((cx + r * np.cos(a), cy + r * np.sin(a), z1)) for a in s])
        bot_front = np.array([uv((cx + r * np.cos(a), cy + r * np.sin(a), z0)) for a in f])
        sil = np.vstack([bot_front, top_back])
        depth = proj((cx, cy, 0.5 * (z0 + z1)))[2] + depth_bias
        topc = top if top is not None else shade(color, 1.06)

        def fn(ax):
            if ghost:
                kw = dict(fc=GHOST_FILL, ec=PLANNED, lw=lw, ls=(0, (2.2, 1.4)), zorder=1)
                ax.add_patch(Polygon(sil, closed=True, **kw))
                ax.add_patch(Polygon(topr, closed=True, **kw))
            else:
                ax.add_patch(Polygon(sil, closed=True, fc=shade(color, 0.92), ec=INK,
                                     lw=lw, joinstyle="round", zorder=1))
                ax.add_patch(Polygon(topr, closed=True, fc=topc, ec=INK, lw=lw,
                                     joinstyle="round", zorder=1))

        del bot
        self.add(depth, fn, layer)
        return np.array([cx, cy, z1])

    def cone(self, cx, cy, z_tip, z_base, r_base, color="#f2f2f2", layer=1,
             lw=LW * 0.8, depth_bias=0.0, n=48):
        """Downward-pointing cone (a pipette tip): base ring at z_base."""
        t = np.linspace(0, 2 * np.pi, n, endpoint=False)
        base = np.array([uv((cx + r_base * np.cos(a), cy + r_base * np.sin(a), z_base))
                         for a in t])
        tip = uv((cx, cy, z_tip))
        # silhouette = convex hull of the base ellipse and the tip point
        pts = np.vstack([base, tip])
        hull = _convex_hull(pts)
        depth = proj((cx, cy, 0.5 * (z_tip + z_base)))[2] + depth_bias

        def fn(ax):
            ax.add_patch(Polygon(hull, closed=True, fc=color, ec=INK, lw=lw,
                                 joinstyle="round", zorder=1))
            ax.add_patch(Polygon(base, closed=True, fc=shade(color, 0.85), ec=INK,
                                 lw=lw * 0.8, zorder=1))

        self.add(depth, fn, layer)

    def line(self, pts3, color=INK, lw=LW, ls="-", layer=1, depth=None):
        pts = np.array([uv(p) for p in pts3])
        d = depth if depth is not None else np.mean([proj(p)[2] for p in pts3])

        def fn(ax):
            ax.plot(pts[:, 0], pts[:, 1], color=color, lw=lw, ls=ls,
                    solid_capstyle="round", zorder=1)

        self.add(d, fn, layer)


def _convex_hull(pts):
    """Monotone-chain convex hull of 2-D points (counter-clockwise)."""
    pts = sorted(map(tuple, pts))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return np.array(lower[:-1] + upper[:-1])


# ---------------------------------------------------------------------------
# the CubXL
# ---------------------------------------------------------------------------
ALU = "#c9ccd1"  # extrusions and plates
DARK = "#5d6066"  # motors, gantry side plates
BLACK_PLA = "#6b6e73"  # black printed parts, lightened so edges stay visible
BLUE = "#3f6eb5"  # Genmitsu end plates
ACRYLIC = "#edf1f4"  # slotted clear deck
SLOT = "#cfd8de"
WHITE_PLA = "#f6f4ee"
GLASS = "#e9f1f6"
CAP = "#b8463c"  # cap bodies (printed, PDMS-filled)
STEEL = "#d2d4d6"  # the steel disc the magnet lifts
P20 = "#d8d8d8"
PSTAT = "#d5d7da"  # EZstat Pro case

# head pose (capper = reference tool, CubOS offsets from the October yaml)
VIAL_X = 136.668
VIAL_PITCH = 33.0  # vial_1 y 45 -> vial_2 y 78
VIAL_Y0 = 45.0
OPEN_VIAL = 1  # vial_2 is open; its cap is on the magnet
CAPPER_XY = (VIAL_X, VIAL_Y0 + OPEN_VIAL * VIAL_PITCH)
PIPETTE_DXY = (55.0, 11.0)
HEADCAM_DXY = (-40.0, 10.0)
HEAD_Z = 104.0  # underside of the electromagnet (the cap it holds hangs below)
VIAL_TOP = 61.0  # 20 mL vial rim; a cap adds 12 mm
# Cubware's 480 x 490 mm slotted deck; CubOS (0, 0) is 142 mm in from its
# left edge and 38 mm in from its front edge
DECK = (-142.0, 338.0, -38.0, 452.0)


def build():
    """The scene, plus named 3-D anchor points for the callouts.

    Layers, painted in order: 0 base, 1 labware behind the head, 2 gantry
    frame, 3 head (in the order added), 4 labware in front of the head, 5
    things beside the machine. Planned parts (dashed ghosts) paint in layer 1.
    """
    s = Scene()
    A = {}  # anchors
    cx, cy = CAPPER_XY
    x0d, x1d, y0d, y1d = DECK

    # -- base, back to front -------------------------------------------------
    for xm in (-196, 351):  # Y motors behind the back end plates
        s.box(xm, xm + 40, 486, 528, -38, 4, color=DARK, layer=0)
    s.box(-205, -155, -60, 478, -50, 22, color=ALU, layer=0)  # left Y axis
    s.box(-192, -168, -54, 472, 22, 30, color="#9fa5ab", layer=0)
    for xp in (-212, 343):  # back end plates
        s.box(xp, xp + 64, 478, 486, -56, 40, color=BLUE, layer=0)
    s.box(-155, 345, 452, 476, -46, -6, color=ALU, layer=0)  # back cross rail
    s.box(x0d, x1d, y0d, y1d, -6, 0, color=ACRYLIC, layer=0)
    deck_slots(s)
    s.box(-155, 345, -64, y0d, -46, -6, color=ALU, layer=0)  # front cross rail
    s.box(345, 395, -60, 478, -50, 22, color=ALU, layer=0)  # right Y axis
    s.box(358, 382, -54, 472, 22, 30, color="#9fa5ab", layer=0)
    for xp in (-212, 343):  # front end plates
        s.box(xp, xp + 64, -68, -60, -56, 40, color=BLUE, layer=0)

    # -- deck labware ------------------------------------------------------
    vys = VIAL_Y0 + VIAL_PITCH * np.arange(9)  # 9-cup column, 6 vials loaded
    s.box(VIAL_X - 15, VIAL_X + 15, vys[0] - 15, vys[-1] + 15, 0, 5, color=BLACK_PLA,
          layer=1)
    for k in sorted(range(9), key=lambda k: -vys[k]):  # back to front
        vy = vys[k]
        layer = 1 if vy > cy + 1 else 4
        s.cylinder(VIAL_X, vy, 5, 28, 16.5, color=BLACK_PLA, layer=layer, n=60)
        if k < 6:
            s.cylinder(VIAL_X, vy, 28, VIAL_TOP, 14, color=GLASS, layer=layer, n=60)
            if k != OPEN_VIAL:
                cap(s, VIAL_X, vy, VIAL_TOP, layer)
    A["vials"] = (VIAL_X - 14, vys[0], 45)
    A["rack"] = (VIAL_X - 15, vys[0] - 15, 3)

    tx0, ty0, pitch = 291.332, 89.0, 8.5  # 2 x 15 tip rack, A1; rows run +y
    s.box(tx0 - pitch - 10, tx0 + 10, ty0 - 9, ty0 + 14 * pitch + 9, 0, 60,
          color=WHITE_PLA, layer=4)
    for row in range(14, -1, -1):
        for col in (1, 0):
            s.cylinder(tx0 - pitch * col, ty0 + pitch * row, 60, 67, 3.1,
                       color="#fbfbfb", layer=4, lw=0.3, n=24)
    A["tips"] = (tx0 + 10, ty0 + 2 * pitch, 40)

    # -- gantry frame: blue side plates, X beam at the back, X motor on the left
    gy = cy + 108  # the beam sits behind the head
    for xp in (-217, 395):
        s.box(xp, xp + 12, gy - 72, gy + 72, -30, 214, color=BLUE, layer=2)
    s.box(-205, 395, gy - 30, gy + 30, 112, 212, color=ALU, layer=2)  # X beam
    for zz in (137, 162, 187):  # its T-slots
        s.line([(-205, gy - 30.2, zz), (395, gy - 30.2, zz)], color="#8f969d", lw=0.35,
               layer=2)
    s.box(-262, -217, gy - 22, gy + 22, 140, 184, color=DARK, layer=2)  # X motor
    A["gantry"] = (300, gy - 30, 200)
    A["xmotor"] = (-262, gy - 22, 170)

    # -- head ----------------------------------------------------------------
    plate_x0, plate_x1 = cx - 78, cx + 77  # 155 mm black pegboard
    py_front = gy - 83  # front face of the tool plate
    hx = 0.5 * (plate_x0 + plate_x1)
    s.box(hx - 40, hx + 40, gy - 75, gy - 30, HEAD_Z - 4, HEAD_Z + 146, color=ALU,
          layer=3)  # Z axis
    s.box(plate_x0, plate_x1, py_front, gy - 75, HEAD_Z + 50, HEAD_Z + 190,
          color=BLACK_PLA, layer=3)  # tool plate
    # (the pegboard's slots are left out: at print size they read as dashes,
    # and dashes mean "planned" here)
    # Arduino Uno with a proto-shield breadboard (capper and pipette driver)
    s.box(cx - 18, cx + 36, py_front - 4, py_front, HEAD_Z + 100, HEAD_Z + 168,
          color="#2f6db0", layer=3)
    s.box(cx - 10, cx + 26, py_front - 12, py_front - 4, HEAD_Z + 112, HEAD_Z + 150,
          color="#fbfbfb", layer=3)
    A["arduino"] = (cx - 10, py_front - 12, HEAD_Z + 130)
    # cam0 on its mast (deck overview), cam1 at the foot of the plate
    mx = cx - 22
    s.box(mx - 6, mx + 6, py_front - 10, py_front, HEAD_Z + 190, HEAD_Z + 300,
          color=BLACK_PLA, layer=3)
    s.box(mx - 15, mx + 15, py_front - 26, py_front, HEAD_Z + 300, HEAD_Z + 326,
          color=BLACK_PLA, layer=3)
    s.cylinder(mx, py_front - 16, HEAD_Z + 292, HEAD_Z + 300, 6, color=INK, layer=3,
               n=36)
    A["cam0"] = (mx - 15, py_front - 26, HEAD_Z + 316)
    kx = cx + HEADCAM_DXY[0]
    s.box(kx - 14, kx + 14, py_front - 22, py_front, HEAD_Z + 44, HEAD_Z + 70,
          color=BLACK_PLA, layer=3)
    s.cylinder(kx, py_front - 12, HEAD_Z + 36, HEAD_Z + 44, 6, color=INK, layer=3, n=36)
    A["cam1"] = (kx - 14, py_front - 22, HEAD_Z + 58)

    # capper: printed arm, 50 N electromagnet, IR break-beam pair at its mouth
    s.box(cx - 10, cx + 10, cy, py_front, HEAD_Z + 30, HEAD_Z + 48, color=BLACK_PLA,
          layer=3)
    s.cylinder(cx, cy, HEAD_Z, HEAD_Z + 40, 13, color=DARK, layer=3)
    cap(s, cx, cy, HEAD_Z - 12, 3)  # the cap it is holding
    for sx in (cx - 22, cx + 17):
        s.box(sx, sx + 5, cy - 4, cy + 4, HEAD_Z - 10, HEAD_Z + 12, color=INK, layer=3)
    A["capper"] = (cx - 13, cy, HEAD_Z + 26)
    A["irbeam"] = (cx - 22, cy - 4, HEAD_Z - 2)

    # Opentrons P20 single-channel GEN2 on the right edge, tip on
    px, py = cx + PIPETTE_DXY[0], cy + PIPETTE_DXY[1]
    s.box(px - 17, px + 17, py - 14, py_front, HEAD_Z + 18, HEAD_Z + 190, color="#3b3d41",
          layer=3)
    s.cylinder(px, py, HEAD_Z - 8, HEAD_Z + 18, 4.6, color="#9a9da2", layer=3, n=36)
    s.cone(px, py, HEAD_Z - 43, HEAD_Z - 8, 3.7, layer=3)
    A["pipette"] = (px + 17, py - 14, HEAD_Z + 150)

    # -- beside the machine: controller box with the E-stop, potentiostat ------
    s.box(455, 655, 90, 300, -50, 12, color="#3f4247", layer=5)  # controller
    s.cylinder(625, 110, 12, 24, 9, color="#c8352b", layer=5, n=36)  # E-stop
    A["estop"] = (634, 110, 20)
    s.box(565, 700, -80, 45, -50, 22, color=PSTAT, layer=5)  # EZstat Pro
    for k in range(3):  # cell-lead sockets
        s.cylinder(595 + 22 * k, -80, 22, 26, 3.2, color=INK, layer=5, n=24)
    A["pstat"] = (700, -20, 0)

    # -- planned (dashed ghosts) ---------------------------------------------
    # DAL PR #180: 4-station O-ring corrosion tray at the back of the deck
    s.box(170, 290, 225, 262, 0, 14, ghost=True, layer=1)
    for k in range(4):
        s.cylinder(185 + 30 * k, 243.5, 14, 18, 9, ghost=True, layer=1, n=36)
    A["corrosion"] = (290, 243, 10)
    # byu-vcl #213 / DAL #148: OpenRAMAN spectrometer on the free left strip
    s.box(-125, 25, -25, 275, 0, 50, ghost=True, layer=1)
    A["raman"] = (-125, 30, 25)

    return s, A


def cap(s, x, y, z0, layer):
    """Magnetic cap: printed, PDMS-filled body with a steel disc on top."""
    s.cylinder(x, y, z0, z0 + 10, 14.5, color=CAP, layer=layer, n=60)
    s.cylinder(x, y, z0 + 10, z0 + 12, 9.5, color=STEEL, layer=layer, n=60)


def deck_slots(s):
    """The slotted deck: 9.8 x 24.8 mm slots, long axis along y."""
    w, l = 9.8, 24.8
    t = np.linspace(0, np.pi, 10)
    outline = np.concatenate([
        np.stack([w / 2 * np.cos(t), (l - w) / 2 + w / 2 * np.sin(t)], 1),
        np.stack([-w / 2 * np.cos(t), -(l - w) / 2 - w / 2 * np.sin(t)], 1),
    ])
    x0d, x1d, y0d, y1d = DECK
    for sx in np.linspace(x0d + 20, x1d - 20, 18):
        for sy in np.linspace(y0d + 26, y1d - 26, 11):
            pts = np.array([uv((sx + dx, sy + dy, 0.05)) for dx, dy in outline])
            s.add(0, (lambda p: lambda ax: ax.add_patch(
                Polygon(p, closed=True, fc=SLOT, ec="#aab6bf", lw=0.25, zorder=1)))(pts),
                layer=0)


# ---------------------------------------------------------------------------
# callouts
# ---------------------------------------------------------------------------
# (anchor key, label, side, implemented?). Each column is listed top to
# bottom, in an order that keeps the leaders from crossing. Evidence for
# every row: README.md.
CALLOUTS = [
    ("cam0", "Deck-overview\ncamera", "L", True),
    ("cam1", "Head camera", "L", True),
    ("capper", "Magnetic decapping\nand recapping", "L", True),
    ("irbeam", "IR cap-capture check", "L", True),
    ("raman", "OpenRAMAN dock\n(planned)", "L", False),
    ("vials", "9-vial holder,\nmagnetic caps", "L", True),
    ("pipette", "Pipetting\n(Opentrons P20 GEN2)", "R", True),
    ("gantry", "CubOS gantry control,\nremote runs", "R", True),
    ("corrosion", "Cu corrosion cell\n(planned)", "R", False),
    ("tips", "Tip pickup and ejection", "R", True),
    ("estop", "Hardware E-stop", "R", True),
    ("pstat", "Remote-run\npotentiostat", "R", True),
]

FS = 8.0  # label size, pt
LEADING = 1.12  # line spacing of two-line labels
DOT = 2.0  # anchor dot, pt
GAP_IN = 0.05  # label to model, in
SHOULDER_IN = 0.07  # horizontal stub of each leader, in
MARGIN_IN = 0.03  # figure edge to label, in
PAD_IN = 0.05  # between labels in a column, in


def text_size_in(fig, text, **kw):
    t = fig.text(0, 0, text, fontsize=FS, linespacing=LEADING, **kw)
    bb = t.get_window_extent(fig.canvas.get_renderer())
    t.remove()
    return bb.width / fig.dpi, bb.height / fig.dpi


def spread(desired, heights, lo, hi, pad):
    """1-D label placement for one column, listed top to bottom.

    Each label centre sits as close to its anchor's height as it can while
    keeping the listed order, `pad` clear of its neighbours, inside [lo, hi].
    """
    y = np.asarray(desired, float).copy()
    h = np.asarray(heights, float)
    y[0] = min(y[0], hi - h[0] / 2)
    for i in range(1, len(y)):
        y[i] = min(y[i], y[i - 1] - (h[i - 1] + h[i]) / 2 - pad)
    if y[-1] - h[-1] / 2 < lo:
        y[-1] = lo + h[-1] / 2
        for i in range(len(y) - 2, -1, -1):
            y[i] = max(y[i], y[i + 1] + (h[i] + h[i + 1]) / 2 + pad)
    return y


def leader(ax, tx, ty, a, side, impl, scale):
    color = INK if impl else PLANNED
    ls = "-" if impl else (0, (3.0, 2.0))
    d = 1 if side == "L" else -1
    sx, kx = tx + d * 0.02 * scale, tx + d * SHOULDER_IN * scale
    ax.plot([sx, kx, a[0]], [ty, ty, a[1]], color=color, lw=0.6, ls=ls,
            solid_joinstyle="round", solid_capstyle="round", zorder=4)
    ax.plot(*a, "o", ms=DOT, mfc=color, mec="white", mew=0.4, zorder=6)


def legend(ax, x, y, scale):
    """Two-entry key, (x, y) = left end of the top entry, data units."""
    dy = 1.5 * FS / 72 * scale
    for k, (impl, text) in enumerate(((True, "Implemented and tested"),
                                      (False, "Planned (not yet built)"))):
        yy = y - k * dy
        color = INK if impl else PLANNED
        ax.plot([x, x + 0.22 * scale], [yy, yy], color=color, lw=0.6,
                ls="-" if impl else (0, (3.0, 2.0)), zorder=4)
        ax.text(x + 0.27 * scale, yy, text, ha="left", va="center", fontsize=FS - 0.5,
                color=color, style="normal" if impl else "italic", zorder=5)


def main():
    scene, anchors = build()
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN))
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_axis_off()
    scene.draw(ax)
    (u0, v0), (u1, v1) = ax.dataLim.get_points()

    rows = []
    for key, text, side, impl in CALLOUTS:
        style = "normal" if impl else "italic"
        w_in, h_in = text_size_in(fig, text, style=style)
        rows.append(dict(text=text, side=side, impl=impl, style=style, w=w_in, h=h_in,
                         a=uv(anchors[key])))
    w = {sd: max(r["w"] for r in rows if r["side"] == sd) for sd in "LR"}
    avail_w = FIG_W_IN - 2 * MARGIN_IN - w["L"] - w["R"] - 2 * (GAP_IN + SHOULDER_IN)
    avail_h = FIG_H_IN - 0.06
    scale = max((u1 - u0) / avail_w, (v1 - v0) / avail_h)  # screen mm per inch
    left = u0 - (MARGIN_IN + w["L"] + GAP_IN + SHOULDER_IN) * scale
    bottom = 0.5 * (v0 + v1) - 0.5 * FIG_H_IN * scale
    ax.set_xlim(left, left + FIG_W_IN * scale)
    ax.set_ylim(bottom, bottom + FIG_H_IN * scale)
    ax.set_aspect("equal")

    lo, hi = bottom + 0.05 * scale, bottom + (FIG_H_IN - 0.05) * scale
    for sd in "LR":
        sub = [r for r in rows if r["side"] == sd]
        ys = spread([r["a"][1] for r in sub], [r["h"] * scale for r in sub],
                    lo, hi, PAD_IN * scale)
        tx = (u0 - (GAP_IN + SHOULDER_IN) * scale if sd == "L"
              else u1 + (GAP_IN + SHOULDER_IN) * scale)
        for r, ty in zip(sub, ys):
            ax.text(tx, ty, r["text"], ha="right" if sd == "L" else "left", va="center",
                    fontsize=FS, linespacing=LEADING, color=INK if r["impl"] else PLANNED,
                    style=r["style"], ma="right" if sd == "L" else "left", zorder=5)
            leader(ax, tx, ty, r["a"], sd, r["impl"], scale)
    legend(ax, left + MARGIN_IN * scale, bottom + 0.27 * scale, scale)

    for ext, kw in (("pdf", {}), ("png", {"dpi": 300})):
        fig.savefig(HERE / f"cubxl_schematic.{ext}", **kw)
    plt.close(fig)


if __name__ == "__main__":
    main()

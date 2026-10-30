"""Draw the stirrer's wiring diagram for BUILD.md stage 5: the CubXL's Arduino Uno, the JST-XH
pair, the cable, the junction board hole by hole, the fan, the MOSFET and the Hall sensor.

    python hardware/vial-stirrer-cubxl/wiring_diagram.py

writes img/wiring_uno.png and prints the hole list that BUILD.md stage 5 gives. Matplotlib
only. It is drawn in the style of the Tic T500 figure (cubos/docs/_static/tic_t500_wiring.py).

check() runs first and makes sure the picture is the circuit. The leads, wires and solder
bridges in PARTS, LANDINGS and BRIDGES have to join exactly the six nodes of BUILD.md's
netlist, and the cable's four cores have to reach the Uno pins the stirrer firmware uses,
none of them a pin the capper or the pipette already has. No hole may hold two leads, no
lead may sit under a part's body, no two bodies may overlap at the sizes in SIZE (the 100 nF is
a 1206 chip, BOM item 13), every part has to lie flat at a lead spacing it can take, and the
MOSFET's legs have to go straight into column H in gate, drain, source order. fit() then
checks that the piece of board fits on the rails of both bases. If any of that fails, the script stops instead of drawing.

Where the numbers come from:
- Uno R3 header positions: Arduino's 0.1 in grid, with the 0.16 in step between D7 and D8.
- Pin orders: BUILD.md's pinout table (IRLZ44N printed face toward you: G D S; US1881 marked
  face toward you: VDD GND OUT).
- The board: BOM item 10's strips are 20 x 80 mm with 6 x 28 holes, so the board is a piece 8
  holes long and the strip's full 6 holes (20 mm) wide (the listing's photos, 2026-10-29).
- The rails, the stop, the notch and where the MOSFET lies: onshape/vial_stirrer.fs, and for
  the compact base compact/build_compact.py. The MOSFET lies flat, printed face up, tab toward
  +X, so seen from above its gate is the lead nearest +Y, the top of the figure.
"""

import math
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patheffects as pe  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "img" / "wiring_uno.png"

C = {
    "5V": "#d62728",
    "GND": "#262626",
    "PWM": "#1fa493",
    "GATE": "#e0609f",
    "DRAIN": "#e8890c",
    "HALL": "#1f5fbf",
    "usb": "#5b6b7b",
    "board": "#2f6b45",
    "board_edge": "#1d4a2e",
    "pad": "#d8d2bf",
    "uno": "#2b7c99",
    "uno_edge": "#1b5568",
    "lead": "#a9a9ad",
}

# --- the circuit: BUILD.md stage 5, "The same circuit as six nodes" ----------------------------
NETLIST = {
    "5V": ["cable 1", "fan red", "1N5819 cathode", "US1881 pin 1", "10 k Hall pull-up", "100 nF"],
    "GND": ["cable 2", "IRLZ44N pin 3", "US1881 pin 2", "10 k gate pull-down", "100 nF"],
    "PWM": ["cable 3", "100 R"],
    "GATE": ["100 R", "IRLZ44N pin 1", "10 k gate pull-down"],
    "DRAIN": ["fan black", "1N5819 anode", "IRLZ44N pin 2"],
    "HALL": ["cable 4", "US1881 pin 3", "10 k Hall pull-up"],
}
# cable core = JST-XH pin -> Uno pin (BUILD.md pinout table)
UNO_PIN = {1: "5V", 2: "GND", 3: "D10", 4: "D2"}
CORE_NET = {1: "5V", 2: "GND", 3: "PWM", 4: "HALL"}

# Uno R3 headers, inches from the board's lower-left corner with the USB at the left
UNO_TOP = [("SCL", 0.84), ("SDA", 0.94), ("AREF", 1.04), ("GND", 1.14), ("13", 1.24), ("12", 1.34),
           ("11", 1.44), ("10", 1.54), ("9", 1.64), ("8", 1.74), ("7", 1.90), ("6", 2.00),
           ("5", 2.10), ("4", 2.20), ("3", 2.30), ("2", 2.40), ("1", 2.50), ("0", 2.60)]
UNO_BOTTOM = [("", 1.10), ("IOREF", 1.20), ("RESET", 1.30), ("3.3V", 1.40), ("5V", 1.50),
              ("GND", 1.60), ("GND", 1.70), ("VIN", 1.80), ("A0", 2.00), ("A1", 2.10),
              ("A2", 2.20), ("A3", 2.30), ("A4", 2.40), ("A5", 2.50)]
# README, Driving it from the Uno: the PANDA firmware uses D3-D7, D9, D11 and A0-A4, and D0 and D1
# carry the USB serial
UNO_BUSY = {"3", "4", "5", "6", "7", "9", "11", "A0", "A1", "A2", "A3", "A4", "0", "1"}
UNO_STIR = {("T", 1.54): "PWM", ("T", 2.40): "HALL", ("B", 1.50): "5V", ("B", 1.60): "GND"}

# --- the junction board, hole by hole ------------------------------------------------------------
# A hole is (column, row): columns A-H run -X -> +X (cable end to MOSFET end) and rows 1-6 run
# +Y -> -Y, so this is the board seen from above, +X to the right, as it sits in the base.
# The strip is 6 holes wide, so the 6 rows are its whole width and its margins rest on the rails.
NCOL, NROW = 8, 6
PITCH = 2.54
STRIP_W = 20.0                  # BOM item 10: 20 x 80 mm strips, 6 x 28 holes
# Parts on top: ref, kind, value, and (hole, terminal) for each end. A resistor's leads are 4 holes
# apart (10.16 mm for a 6.3 mm body) and the diode's 3 or 4, each lying flat between its holes. The
# 100 nF is a 1206 chip (BOM item 13) soldered on top across the pads of two neighbouring holes. A
# leaded 100 nF has a body about 4 mm across: laid flat beside E5-E6 it would ride up on R3's end.
PARTS = [
    ("R1", "res", "100 Ω", ((1, 0), "100 R"), ((5, 0), "100 R")),
    ("R2", "res", "10 k", ((6, 0), "10 k gate pull-down"), ((6, 4), "10 k gate pull-down")),
    ("R3", "res", "10 k", ((2, 1), "10 k Hall pull-up"), ((2, 5), "10 k Hall pull-up")),
    ("D1", "diode", "1N5819", ((5, 2), "1N5819 anode"), ((5, 5), "1N5819 cathode")),
    ("C1", "smd", "100 nF", ((4, 4), "100 nF"), ((4, 5), "100 nF")),
]
# Body sizes, mm, along the leads x across: 1/4 W resistor, DO-41, 1206 chip
SIZE = {"res": (6.3, 2.4), "diode": (4.8, 2.6), "smd": (3.2, 1.6)}
# Wires and legs that end in a hole
LANDINGS = [
    ("cable 1", (0, 5)), ("cable 2", (0, 4)), ("cable 3", (0, 0)), ("cable 4", (0, 2)),
    ("US1881 pin 1", (1, 5)), ("US1881 pin 2", (1, 4)), ("US1881 pin 3", (1, 2)),
    ("fan red", (6, 5)), ("fan black", (4, 2)),
    ("IRLZ44N pin 1", (7, 1)), ("IRLZ44N pin 2", (7, 2)), ("IRLZ44N pin 3", (7, 3)),
]
# Solder bridges between neighbouring holes, underneath. Rows 5 and 6 are the GND and 5V rails.
BRIDGES = [
    ((0, 0), (1, 0)),                                                          # PWM
    ((5, 0), (6, 0)), ((6, 0), (7, 0)), ((7, 0), (7, 1)),                      # GATE
    ((4, 2), (5, 2)), ((5, 2), (6, 2)), ((6, 2), (7, 2)),                      # DRAIN
    ((0, 4), (1, 4)), ((1, 4), (2, 4)), ((2, 4), (3, 4)), ((3, 4), (4, 4)),    # GND rail
    ((4, 4), (5, 4)), ((5, 4), (6, 4)), ((6, 4), (7, 4)), ((7, 4), (7, 3)),
    ((0, 5), (1, 5)), ((1, 5), (2, 5)), ((2, 5), (3, 5)), ((3, 5), (4, 5)),    # 5V rail
    ((4, 5), (5, 5)), ((5, 5), (6, 5)),
    ((0, 2), (1, 2)), ((1, 2), (2, 2)), ((2, 2), (2, 1)),                      # HALL
]
# Where the board goes, against the stop on the two rails at -X: the -X wall's inner face and the
# stop's -X face (vial_stirrer.fs makeBase; build_compact.py moves both 0.5 mm in), the rails at
# |y| 7.4-8.9, and the fan posts, R4 at (+-16, +-16).
BASES = {"56 x 56 mm base": (-23.5, -1.6), "compact base": (-22.9, -1.1)}
RAIL_Y = (7.4, 8.9)
FAN_POST, FAN_POST_R = 16.0, 4.0


def hole_name(h):
    return f"{'ABCDEFGH'[h[0]]}{h[1] + 1}"


def body_holes(part):
    """Holes a part's body lies over (no lead may go in them): those between its ends."""
    (a, _), (b, _) = part[3], part[4]
    dc, dr = b[0] - a[0], b[1] - a[1]
    n = abs(dc) + abs(dr)
    sc, sr = (dc > 0) - (dc < 0), (dr > 0) - (dr < 0)
    return [(a[0] + sc * i, a[1] + sr * i) for i in range(1, n)]


def body_box(part):
    """A part's body in plan, mm: (x, y, half width, half height), x along the columns, y down the rows."""
    (a, _), (b, _) = part[3], part[4]
    length, width = SIZE[part[1]]
    x, y = (a[0] + b[0]) / 2 * PITCH, (a[1] + b[1]) / 2 * PITCH
    return (x, y, width / 2, length / 2) if a[0] == b[0] else (x, y, length / 2, width / 2)


def check():
    """Stop unless LAYOUT is BUILD.md's circuit and can be built as drawn."""
    used = {}
    for part in PARTS:
        ref, kind = part[0], part[1]
        (a, _), (b, _) = part[3], part[4]
        if a[0] != b[0] and a[1] != b[1]:
            raise SystemExit(f"{ref} does not lie along a row or a column")
        span = abs(a[0] - b[0]) + abs(a[1] - b[1])
        ok = {"res": {4}, "diode": {3, 4}, "smd": {1}}[kind]
        if span not in ok:
            raise SystemExit(f"{ref}: leads {span} holes apart, needs {sorted(ok)}")
        for h, term in (part[3], part[4]):
            if h in used:
                raise SystemExit(f"{hole_name(h)} holds both {used[h]} and {term}")
            used[h] = term
    for term, h in LANDINGS:
        if h in used:
            raise SystemExit(f"{hole_name(h)} holds both {used[h]} and {term}")
        used[h] = term
    covered = {}
    for part in PARTS:
        for h in body_holes(part):
            if not (0 <= h[0] < NCOL and 0 <= h[1] < NROW):
                raise SystemExit(f"{part[0]}'s body runs off the board at {h}")
            if h in used:
                raise SystemExit(f"{part[0]}'s body lies over {hole_name(h)}, which holds {used[h]}")
            if h in covered:
                raise SystemExit(f"{part[0]} and {covered[h]} both lie over {hole_name(h)}")
            covered[h] = part[0]
    # parts side by side a column apart: their bodies, not just their holes, must not overlap
    for i, p in enumerate(PARTS):
        for q in PARTS[i + 1:]:
            (x1, y1, w1, h1), (x2, y2, w2, h2) = body_box(p), body_box(q)
            if abs(x1 - x2) < w1 + w2 and abs(y1 - y2) < h1 + h2:
                raise SystemExit(f"{p[0]}'s body and {q[0]}'s overlap, at the sizes in SIZE")
    parent = {(c, r): (c, r) for c in range(NCOL) for r in range(NROW)}

    def find(h):
        while parent[h] != h:
            parent[h] = parent[parent[h]]
            h = parent[h]
        return h

    for u, v in BRIDGES:
        if abs(u[0] - v[0]) + abs(u[1] - v[1]) != 1:
            raise SystemExit(f"bridge {hole_name(u)}-{hole_name(v)} is not between neighbours")
        parent[find(u)] = find(v)
    groups = {}
    for h, term in used.items():
        groups.setdefault(find(h), Counter())[term] += 1
    want = {net: Counter(terms) for net, terms in NETLIST.items()}
    found = {}
    for root, terms in groups.items():
        match = [net for net, w in want.items() if w == terms]
        if not match:
            raise SystemExit(f"a node joins {dict(terms)}, which is not in BUILD.md's netlist")
        found[match[0]] = root
    if set(found) != set(want):
        raise SystemExit(f"missing nodes: {sorted(set(want) - set(found))}")
    # every bridged hole belongs to a node with terminals: no stray copper
    for u, v in BRIDGES:
        if find(u) not in found.values():
            raise SystemExit(f"bridge {hole_name(u)}-{hole_name(v)} joins nothing")
    # the cable's cores go to the Uno pins BUILD.md names, which the PANDA firmware leaves free
    labels = {("T", x): n for n, x in UNO_TOP} | {("B", x): n for n, x in UNO_BOTTOM}
    for core, pin in UNO_PIN.items():
        if f"cable {core}" not in NETLIST[CORE_NET[core]]:
            raise SystemExit(f"cable {core} should be {CORE_NET[core]}")
        drawn = [labels[key] for key, net in UNO_STIR.items() if net == CORE_NET[core]]
        if drawn != [pin.removeprefix("D")]:
            raise SystemExit(f"cable {core} is drawn to Uno pin {drawn}, BUILD.md says {pin}")
        if drawn[0] in UNO_BUSY:
            raise SystemExit(f"Uno pin {pin} is already the capper's or the pipette's")
    # the MOSFET lies printed face up with its legs straight into column H: G, D, S from the top
    legs = [dict(LANDINGS)[f"IRLZ44N pin {i}"] for i in (1, 2, 3)]
    if [c for c, _ in legs] != [NCOL - 1] * 3 or [r - legs[0][1] for _, r in legs] != [0, 1, 2]:
        raise SystemExit(f"the MOSFET's legs {[hole_name(h) for h in legs]} are not straight into column H")
    net_of = {}
    for net, root in found.items():
        for h in parent:
            if find(h) == root and (h in used or any(h in e for e in BRIDGES)):
                net_of[h] = net
    return net_of


def fit():
    """Stop unless the piece fits on the rails of both bases, pushed against the stop. It is
    snapped through the next column of holes at each end, so it is NCOL pitches long, and it is
    the strip's full width. Returns, by base, the room left at the -X wall and the gap from the
    piece's long edges to the fan posts, in mm."""
    length = NCOL * PITCH
    if STRIP_W / 2 < RAIL_Y[1]:
        raise SystemExit(f"a {STRIP_W} mm board doesn't reach across both rails")
    out = {}
    for name, (wall, stop) in BASES.items():
        spare = stop - wall - length
        dx = max(stop - length + FAN_POST, 0.0, -FAN_POST - stop)    # the -X fan posts, at x = -16
        post = math.hypot(dx, FAN_POST - STRIP_W / 2) - FAN_POST_R
        if spare < 0.2 or post < 0.2:
            raise SystemExit(f"the board doesn't fit the {name}: {spare:.2f} mm left at the wall, "
                             f"{post:.2f} mm from the fan posts")
        out[name] = (spare, post)
    return out


# --- drawing -------------------------------------------------------------------------------------
W, H = 17.4, 11.2
P = 0.54                        # board pitch in figure units (2.54 mm)
MM = P / 2.54                   # figure units per mm, at the board's scale
BX, BY = 8.85, 7.18             # where hole A1 is drawn
FLYING = {                      # leads that come down onto the board from above: marker text, colour
    "US1881 pin 1": ("1", "5V"), "US1881 pin 2": ("2", "GND"), "US1881 pin 3": ("3", "HALL"),
    "fan red": ("+", "5V"), "fan black": ("−", "GND"),
}


def wire(ax, pts, colour, lw=3.0, z=3, halo=3.5):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=C.get(colour, colour), lw=lw, zorder=z, solid_capstyle="round",
            solid_joinstyle="round",
            path_effects=[pe.Stroke(linewidth=lw + halo, foreground="white"), pe.Normal()])


def text(ax, x, y, s, size=11, weight="normal", colour="#1a1a1a", ha="center", va="center", **kw):
    ax.text(x, y, s, fontsize=size, fontweight=weight, color=colour, ha=ha, va=va, **kw)


def chip(ax, x, y, s, colour, ha="center", size=9.5, z=12):
    return ax.text(x, y, s, fontsize=size, fontweight="bold", color="white", ha=ha, va="center", zorder=z,
                   bbox=dict(boxstyle="round,pad=0.25", fc=C.get(colour, colour), ec="none"))


def marker(ax, x, y, s, colour, r=0.13, z=11):
    """A lead that comes down onto the board from above, seen end on."""
    ax.add_patch(Circle((x, y), r, fc=C[colour], ec="white", lw=1.6, zorder=z))
    text(ax, x, y - 0.005, s, 9 if len(s) == 1 else 7.5, "bold", "white", zorder=z + 0.1)


def draw_uno(ax, x0, y0, k):
    """Uno R3 to scale, k units per mm. Returns the stirrer pins' (x, y), by node."""
    mm = 25.4 * k
    ax.add_patch(FancyBboxPatch((x0, y0), 68.58 * k, 53.34 * k, boxstyle="round,pad=0,rounding_size=0.06",
                                fc=C["uno"], ec=C["uno_edge"], lw=2, zorder=1))
    ax.add_patch(Rectangle((x0 - 6.35 * k, y0 + 32 * k), 16.3 * k, 12 * k, fc="#c9c9c9", ec="#555555",
                           lw=1.4, zorder=2))
    text(ax, x0 + 1.8 * k, y0 + 38 * k, "USB-B", 7.5, "bold", "#222222", zorder=3)
    ax.add_patch(Rectangle((x0 - 1.9 * k, y0 + 3.3 * k), 14.9 * k, 9 * k, fc="#222222", ec="#111111",
                           lw=1.2, zorder=2))
    ax.add_patch(Rectangle((x0 + 1.18 * mm, y0 + 0.40 * mm), 1.38 * mm, 0.30 * mm, fc="#1e1e1e",
                           ec="#000000", lw=1, zorder=2))
    text(ax, x0 + 1.87 * mm, y0 + 0.55 * mm, "ATmega328P", 7, colour="#bbbbbb", zorder=3)
    text(ax, x0 + 0.62 * mm, y0 + 1.02 * mm, "UNO", 16, "bold", "#d8eef5", zorder=2)
    pins = {}
    s = 1.95 * k
    for row, yy, labels, split in (("T", 2.0, UNO_TOP, 1.85), ("B", 0.1, UNO_BOTTOM, 1.95)):
        xs = [x for _, x in labels]
        for g in ([x for x in xs if x < split], [x for x in xs if x > split]):
            ax.add_patch(Rectangle((x0 + (g[0] - 0.05) * mm, y0 + (yy - 0.05) * mm), (g[-1] - g[0] + 0.1) * mm,
                                   0.1 * mm, fc="#151515", ec="#151515", lw=0.5, zorder=2))
        for name, x in labels:
            net = UNO_STIR.get((row, x))
            px, py = x0 + x * mm, y0 + yy * mm
            busy = name in UNO_BUSY
            ax.add_patch(Rectangle((px - s / 2, py - s / 2), s, s, fc=C[net] if net else ("#8d8d8d" if busy else "#dcdcdc"),
                                   ec="#111111" if net else "#444444", lw=1.4 if net else 0.6, zorder=4))
            if net:
                pins[net] = (px, py)
            elif name:
                text(ax, px, py + (-0.09 if row == "T" else 0.09), name, 6.3, colour="#9fc4d2" if busy else "#eaf5f9",
                     va="top" if row == "T" else "bottom", rotation=90, zorder=3)
    return pins


def draw_jst(ax, x0, ys, w=0.42):
    """The JST-XH pair, mated: housing (Uno side, recessed contacts) left, plug (cable side) right.
    ys are the pins' heights, pin 1 first."""
    top, bot = max(ys) + 0.2, min(ys) - 0.2
    ax.add_patch(Rectangle((x0, bot), w, top - bot, fc="#f4f1e6", ec="#555555", lw=1.6, zorder=5))
    ax.add_patch(Rectangle((x0 + w, bot + 0.05), w * 0.8, top - bot - 0.1, fc="#ebe6d4", ec="#555555", lw=1.6,
                           zorder=5))
    for i, y in enumerate(ys):
        ax.add_patch(Rectangle((x0 + 0.12, y - 0.07), 0.14, 0.14, fc="#7a7a7a", ec="#444444", lw=0.8, zorder=6))
        text(ax, x0 + w + w * 0.4, y, str(i + 1), 11, "bold", "#222222", zorder=6)
    return x0, x0 + w * 1.8


def draw_break(ax, x, y, h=0.42):
    ax.add_patch(Rectangle((x - 0.06, y - h / 2 - 0.02), 0.12, h + 0.04, fc="white", ec="none", zorder=7))
    for dx in (-0.06, 0.06):
        ax.plot([x + dx - 0.05, x + dx + 0.05], [y - h / 2 - 0.03, y + h / 2 + 0.03], color="#444444", lw=1.6,
                zorder=8)


class Board:
    """The junction board drawn with hole A1 at (x0, y0) and a pitch of p units. mirror=True draws
    the underside as you hold it to solder: turned over left to right, so column A is on the right."""

    def __init__(self, ax, x0, y0, p, nets, mirror=False):
        self.ax, self.x0, self.y0, self.p, self.nets, self.mirror = ax, x0, y0, p, nets, mirror

    def xy(self, h):
        c = NCOL - 1 - h[0] if self.mirror else h[0]
        return self.x0 + c * self.p, self.y0 - h[1] * self.p

    def outline(self):
        """Snapped through the next column of holes at each end, and the strip's full width across."""
        mx, my = 0.5 * self.p, (STRIP_W - (NROW - 1) * PITCH) / 2 / PITCH * self.p
        return self.x0 - mx, self.y0 - (NROW - 1) * self.p - my, (NCOL - 1) * self.p + 2 * mx, \
            (NROW - 1) * self.p + 2 * my

    def draw(self, size=10.5, row_labels=True):
        ax, p = self.ax, self.p
        x0, y0, w, h = self.outline()
        plate = FancyBboxPatch((x0, y0), w, h, boxstyle="round,pad=0,rounding_size=0.03",
                               fc=C["board"], ec=C["board_edge"], lw=2, zorder=1)
        ax.add_patch(plate)
        for r in range(NROW):            # the half holes the snapped ends leave
            for x in (x0, x0 + w):
                for patch in (Circle((x, self.xy((0, r))[1]), 0.27 * p, fc=C["pad"], ec="#b9b29a", lw=0.8 * p / P),
                              Circle((x, self.xy((0, r))[1]), 0.12 * p, fc="#2b2b2b", ec="none")):
                    ax.add_patch(patch)
                    patch.set_zorder(1.5)
                    patch.set_clip_path(plate)
        for c in range(NCOL):
            text(ax, self.xy((c, 0))[0], y0 + h + 0.17 * p / P, "ABCDEFGH"[c], size, "bold", "#333333")
        if row_labels:
            for r in range(NROW):
                text(ax, x0 + w + 0.17 * p / P, self.xy((0, r))[1], str(r + 1), size, "bold", "#333333", zorder=12,
                     bbox=dict(boxstyle="round,pad=0.08", fc="white", ec="none"))
        # solder bridges: underneath, drawn through the board on the top view
        for u, v in BRIDGES:
            (xa, ya), (xb, yb) = self.xy(u), self.xy(v)
            ax.plot([xa, xb], [ya, yb], color=C[self.nets[u]], lw=p * 72 * 0.42, solid_capstyle="round",
                    alpha=1.0 if self.mirror else 0.88, zorder=2)
        for c in range(NCOL):
            for r in range(NROW):
                x, y = self.xy((c, r))
                net = self.nets.get((c, r))
                ax.add_patch(Circle((x, y), 0.27 * p, fc=C["pad"], ec=C[net] if net else "#b9b29a",
                                    lw=(2.2 if net else 0.8) * p / P, zorder=3))
                ax.add_patch(Circle((x, y), 0.12 * p, fc="#2b2b2b", ec="none", zorder=4))

    def lead(self, h, x, y, z=6):
        hx, hy = self.xy(h)
        self.ax.plot([hx, x], [hy, y], color=C["lead"], lw=2.4, solid_capstyle="round", zorder=z)
        self.ax.add_patch(Circle((hx, hy), 0.1 * self.p, fc="#cfcfd2", ec="#6d6d6d", lw=0.8, zorder=z + 0.1))

    def axial(self, part):
        ref, kind, value = part[0], part[1], part[2]
        a, b = part[3][0], part[4][0]
        (xa, ya), (xb, yb) = self.xy(a), self.xy(b)
        horiz = a[1] == b[1]
        L, D = (v * MM for v in SIZE[kind])
        cx, cy = (xa + xb) / 2, (ya + yb) / 2
        n = ((xb - xa) ** 2 + (yb - ya) ** 2) ** 0.5
        ux, uy = (xb - xa) / n, (yb - ya) / n
        self.lead(a, cx - ux * L / 2, cy - uy * L / 2)
        self.lead(b, cx + ux * L / 2, cy + uy * L / 2)
        bw, bh = (L, D) if horiz else (D, L)
        self.ax.add_patch(FancyBboxPatch((cx - bw / 2, cy - bh / 2), bw, bh,
                                         boxstyle=f"round,pad=0,rounding_size={D * 0.45}",
                                         fc="#d9c7a0" if kind == "res" else "#1c1c1c", ec="#3a3a3a", lw=1.4,
                                         zorder=7))
        if kind == "diode":   # silver band at the cathode end
            cath = part[4][0] if "cathode" in part[4][1] else part[3][0]
            kx, ky = self.xy(cath)
            sgn = 1 if (kx - cx) + (ky - cy) > 0 else -1
            bx, by = (cx + sgn * (L / 2 - 0.55 * MM), cy) if horiz else (cx, cy + sgn * (L / 2 - 0.55 * MM))
            sw, sh = (0.8 * MM, D) if horiz else (D, 0.8 * MM)
            self.ax.add_patch(Rectangle((bx - sw / 2, by - sh / 2), sw, sh, fc="#d6d6d6", ec="none", zorder=8))
        shift = 0.0
        if kind == "diode":
            shift = -sgn * 0.5 * MM
        lx, ly = (cx + shift, cy) if horiz else (cx, cy + shift)
        text(self.ax, lx, ly, f"{ref}  {value}", 8.4 if kind == "diode" else 8.6, "bold",
             "#2a2a2a" if kind == "res" else "#f0f0f0", rotation=0 if horiz else 90, zorder=9)

    def smd(self, part):
        """A 1206 chip soldered on top across the pads of two neighbouring holes."""
        ref, value = part[0], part[2]
        a, b = part[3][0], part[4][0]
        (xa, ya), (xb, yb) = self.xy(a), self.xy(b)
        vert = a[0] == b[0]
        cx, cy = (xa + xb) / 2, (ya + yb) / 2
        L, D = (v * MM for v in SIZE["smd"])
        bw, bh = (D, L) if vert else (L, D)
        self.ax.add_patch(Rectangle((cx - bw / 2, cy - bh / 2), bw, bh, fc="#b8955f", ec="#5c4524", lw=1.2, zorder=7))
        e = 0.5 * MM   # the tinned terminations, soldered to the pads
        for s_ in (-1, 1):
            ex, ey = (cx, cy + s_ * (bh - e) / 2) if vert else (cx + s_ * (bw - e) / 2, cy)
            ew, eh = (bw, e) if vert else (e, bh)
            self.ax.add_patch(Rectangle((ex - ew / 2, ey - eh / 2), ew, eh, fc="#d6d6d6", ec="#6d6d6d", lw=0.8,
                                        zorder=7.5))
        text(self.ax, cx, cy, f"{ref} {value.replace(' nF', 'n')}", 6.2, "bold", "#1a1a1a",
             rotation=90 if vert else 0, zorder=9)

    def parts(self):
        for part in PARTS:
            (self.smd if part[1] == "smd" else self.axial)(part)


def draw_mosfet(ax, board, rows, x_body):
    """IRLZ44N lying flat, printed face up, tab toward +X, its legs into column H."""
    ys = [board.xy((7, r))[1] for r in rows]
    yc = ys[1]
    hx = board.xy((7, 0))[0]
    for y in ys:
        ax.plot([hx, x_body], [y, y], color=C["lead"], lw=0.8 * MM * 72, solid_capstyle="butt", zorder=6)
        ax.add_patch(Circle((hx, y), 0.1 * board.p, fc="#cfcfd2", ec="#6d6d6d", lw=0.8, zorder=6.1))
    ax.add_patch(Rectangle((x_body, yc - 5.1 * MM), 9.2 * MM, 10.2 * MM, fc="#1c1c1c", ec="#000000", lw=1.4,
                           zorder=7))
    xt = x_body + 9.2 * MM
    ax.add_patch(Rectangle((xt, yc - 5.1 * MM), 6.4 * MM, 10.2 * MM, fc="#c4c4c8", ec="#6d6d6d", lw=1.4, zorder=6))
    ax.add_patch(Circle((xt + 3.0 * MM, yc), 1.8 * MM, fc="white", ec="#6d6d6d", lw=1.2, zorder=7))
    text(ax, x_body + 5.2 * MM, yc + 0.02, "IRLZ44N", 9.5, "bold", "#f0f0f0", zorder=8)
    for y, lab in zip(ys, ("1 G", "2 D", "3 S")):
        text(ax, x_body + 0.07, y, lab, 8, "bold", "#f0f0f0", ha="left", zorder=8)
    text(ax, xt + 3.2 * MM, yc - 5.1 * MM - 0.14, "tab = drain", 8.5, colour="#555555")
    return xt + 6.4 * MM, yc


def draw_fan(ax, cx, cy, s):
    ax.add_patch(FancyBboxPatch((cx - s / 2, cy - s / 2), s, s, boxstyle="round,pad=0,rounding_size=0.08",
                                fc="#2a2a2a", ec="#111111", lw=1.6, zorder=5))
    ax.add_patch(Circle((cx, cy), s * 0.44, fc="#3c3c3c", ec="#151515", lw=1, zorder=6))
    for i in range(7):
        a = i * 2 * math.pi / 7
        pts = [(cx + s * 0.12 * math.cos(a), cy + s * 0.12 * math.sin(a)),
               (cx + s * 0.42 * math.cos(a + 0.35), cy + s * 0.42 * math.sin(a + 0.35)),
               (cx + s * 0.42 * math.cos(a + 0.75), cy + s * 0.42 * math.sin(a + 0.75))]
        ax.add_patch(Polygon(pts, closed=True, fc="#555555", ec="#222222", lw=0.6, zorder=7))
    ax.add_patch(Circle((cx, cy), s * 0.14, fc="#7a7a7a", ec="#222222", lw=1, zorder=8))
    for dx in (-1, 1):
        for dy in (-1, 1):
            ax.add_patch(Circle((cx + dx * s * 0.4, cy + dy * s * 0.4), s * 0.045, fc="white", ec="#111111",
                                lw=0.8, zorder=8))


def draw_hall(ax, cx, cy, s):
    """US1881 in TO-92UA, marked face toward the viewer; returns the three legs' ends, pin 1 first."""
    w, h = 4.1 * s, 3.0 * s
    pts = [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2 - 0.6 * s),
           (cx + w / 2 - 0.6 * s, cy + h / 2), (cx - w / 2 + 0.6 * s, cy + h / 2), (cx - w / 2, cy + h / 2 - 0.6 * s)]
    ax.add_patch(Polygon(pts, closed=True, fc="#1c1c1c", ec="#000000", lw=1.4, zorder=7))
    text(ax, cx, cy, "1881", 8.5, "bold", "#e8e8e8", zorder=8)
    ends = []
    for i in range(3):
        x = cx + (i - 1) * 1.27 * s
        ax.plot([x, x], [cy - h / 2, cy - h / 2 - 1.6 * s], color=C["lead"], lw=2.2, zorder=6)
        ends.append((x, cy - h / 2 - 1.6 * s))
    return ends


def landing(term):
    return dict(LANDINGS)[term]


def figure(nets):
    fig = plt.figure(figsize=(W, H), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    text(ax, 0.3, 10.88, "Stirrer wiring, Uno version (BUILD.md stage 5): the CubXL's Uno drives the fan from D10 "
         "and counts turns on D2", 15.5, "bold", ha="left")
    text(ax, 0.3, 10.53, "Drawn from BUILD.md's netlist by wiring_diagram.py, which checks this layout against it. "
         "Nothing has been built yet: the junction board is a piece of the 6-hole-wide perfboard strip, 8 × 6 holes.",
         10.5, colour="#444444", ha="left")

    # --- Pi and Uno -------------------------------------------------------------------------------
    ax.add_patch(FancyBboxPatch((0.35, 9.35), 3.6, 0.78, boxstyle="round,pad=0,rounding_size=0.1",
                                fc="#e7f0e7", ec="#3c6e3c", lw=2, zorder=4))
    text(ax, 2.15, 9.87, "Raspberry Pi 5 (CubXL Pi)", 13, "bold", zorder=5)
    text(ax, 2.15, 9.55, "its USB powers the Uno: 5 V, 500 mA fuse", 9.5, zorder=5)
    k = 0.058
    ux, uy = 0.7, 5.6
    pins = draw_uno(ax, ux, uy, k)
    wire(ax, [(0.6, 9.35), (0.6, 9.1), (0.12, 9.1), (0.12, uy + 38 * k), (ux - 6.35 * k, uy + 38 * k)], "usb", lw=5)
    text(ax, 2.68, 4.75, "Arduino Uno R3 on the CubXL", 15, "bold")
    text(ax, 2.68, 4.46, "capper + pipette, PANDA firmware with the stirrer patch", 9.5, colour="#333333")
    text(ax, 2.68, 4.23, "dark grey pins are in use (capper, pipette, USB serial): leave them alone", 8.8,
         colour="#555555")

    # --- JST-XH pair and its Uno-side leads ---------------------------------------------------------
    jx = 5.42
    jy = {1: 6.65, 2: 6.95, 3: 7.25, 4: 7.55}
    x_l, x_r = draw_jst(ax, jx, [jy[1], jy[2], jy[3], jy[4]])
    text(ax, jx + 0.38, jy[4] + 0.42, "JST-XH, 4-pin", 10, "bold")
    s = 1.95 * k
    d2, d10, gnd, v5 = pins["HALL"], pins["PWM"], pins["GND"], pins["5V"]
    wire(ax, [(jx, jy[4]), (5.08, jy[4]), (5.08, 8.92), (d2[0], 8.92), (d2[0], d2[1] + s / 2)], "HALL", lw=2.6)
    wire(ax, [(jx, jy[3]), (d10[0], jy[3]), (d10[0], d10[1] - s / 2)], "PWM", lw=2.6)
    wire(ax, [(jx, jy[2]), (4.96, jy[2]), (4.96, 5.25), (gnd[0], 5.25), (gnd[0], gnd[1] - s / 2)], "GND", lw=2.6)
    wire(ax, [(jx, jy[1]), (5.2, jy[1]), (5.2, 5.05), (v5[0], 5.05), (v5[0], v5[1] - s / 2)], "5V", lw=2.6)
    chip(ax, d2[0], 9.12, "D2: Hall in", "HALL")
    chip(ax, 4.0, jy[3] + 0.2, "D10: fan PWM out", "PWM")
    chip(ax, 3.75, 5.05, "5V", "5V", size=9)
    chip(ax, 4.45, 5.25, "GND", "GND", size=9)

    # --- cable ------------------------------------------------------------------------------------
    board = Board(ax, BX, BY, P, nets)
    yj = board.xy((0, (NROW - 1) / 2))[1]              # the notch, the rails and the stop are centred on the board
    xs = x_r + 0.05
    ys_ = [jy[c] for c in (1, 2, 3, 4)]
    for c in (1, 2, 3, 4):
        wire(ax, [(x_r, jy[c]), (xs + 0.15, jy[c]), (xs + 0.32, 7.1 + 0.06 * (c - 2.5))], CORE_NET[c], lw=2.4,
             halo=2.5)
    ax.add_patch(Rectangle((xs + 0.32, 6.86), 0.14, 0.48, fc="#333333", ec="none", zorder=6))   # heat shrink
    jac = 7.1
    ax.plot([xs + 0.46, 7.3, 7.3, 8.3], [jac, jac, yj, yj], color="#8d8d8d", lw=17, solid_capstyle="butt",
            solid_joinstyle="round", zorder=5)
    draw_break(ax, 7.0, jac)
    text(ax, 7.0, jac + 0.42, "≈ 1.5 m", 9.5, "bold", "#333333")
    text(ax, 7.75, yj - 0.33, "22 AWG × 4", 9, colour="#333333")
    text(ax, (x_l + x_r) / 2 + 0.2, min(ys_) - 0.42, "housing on the Uno side,\nplug on the cable", 8,
         colour="#555555", va="top")
    # the base's -X wall and its 13 mm notch
    bx_, by_, bw_, bh_ = board.outline()
    wx = bx_ - 0.2
    nh = 6.5 * MM
    for ya, yb in ((by_ + bh_ + 0.15, yj + nh), (yj - nh, by_ - 0.15)):
        ax.add_patch(Rectangle((wx - 0.16, yb), 0.16, ya - yb, fc="#b9bec4", ec="#7d848c", lw=1, zorder=2))
    text(ax, wx - 0.26, (yj + nh + by_ + bh_ + 0.15) / 2 + 0.08, "−X wall", 8.5, colour="#555555", ha="right")
    text(ax, wx - 0.45, yj + nh + 0.12, "notch", 8.5, colour="#555555")
    targets = {c: board.xy(landing(f"cable {c}")) for c in (1, 2, 3, 4)}
    up = sorted([c for c in targets if targets[c][1] > yj], key=lambda c: -targets[c][1])
    down = sorted([c for c in targets if targets[c][1] <= yj], key=lambda c: targets[c][1])
    for group, sign in ((up, 1), (down, -1)):
        for i, c in enumerate(group):
            tx, ty = targets[c]
            ex, ey = bx_ - 0.12 + 0.1 * i, yj + sign * 0.07 * (len(group) - i)
            wire(ax, [(8.3, ey), (ex, ey), (ex, ty), (tx, ty)], CORE_NET[c], lw=2.4, halo=2.5, z=9)
            ax.add_patch(Circle((tx, ty), 0.075, fc=C[CORE_NET[c]], ec="white", lw=1, zorder=10))

    # --- board, MOSFET, stop ------------------------------------------------------------------------
    board.draw()
    board.parts()
    for term, (s_, colour) in FLYING.items():
        x, y = board.xy(landing(term))
        marker(ax, x, y, s_, colour)
    stop_x = bx_ + bw_ + 0.42
    legs = [landing(f"IRLZ44N pin {i}") for i in (1, 2, 3)]
    ax.add_patch(Rectangle((stop_x, yj - 5 * MM), 1.2 * MM, 10 * MM, fc="#b9bec4", ec="#7d848c", lw=1, zorder=2))
    text(ax, stop_x + 0.6 * MM, yj + 5 * MM + 0.14, "stop", 8.5, colour="#555555")
    draw_mosfet(ax, board, [r for _, r in legs], stop_x + 0.5)
    g, d, s_ = (hole_name(h) for h in legs)
    for i, line in enumerate((
            "IRLZ44N, flat on the floor past the stop: printed face up,",
            "tab toward +X and touching nothing. Its legs bend up over",
            f"the stop into {g}, {d} and {s_}; short wires work too.")):
        text(ax, stop_x - 0.05, 4.43 - 0.23 * i, line, 9, colour="#222222", ha="left")

    # --- Hall sensor and fan: their leads come down onto the board from above --------------------
    hx, hy = 8.95, 9.62
    ends = draw_hall(ax, hx, hy, 0.15)
    for (ex, ey), dx, term in zip(ends, (-0.27, 0.0, 0.27), ("US1881 pin 1", "US1881 pin 2", "US1881 pin 3")):
        s_, colour = FLYING[term]
        wire(ax, [(ex, ey), (ex, ey - 0.12), (ex + dx, 8.62)], colour, lw=2.2, halo=2.0, z=8)
        marker(ax, ex + dx, 8.62, s_, colour)
        text(ax, ex + dx, 8.38, hole_name(landing(term)), 9, "bold", "#333333")
    for i, (line, size, weight) in enumerate((
            ("US1881 Hall latch", 10, "bold"),
            ("marked face toward you: 1 VDD, 2 GND, 3 OUT.", 9, "normal"),
            ("Glued under the vial holder's floor; its leads", 9, "normal"),
            ("come down the −X wall onto {}, {} and {}.".format(
                *(hole_name(landing(f"US1881 pin {i}")) for i in (1, 2, 3))), 9, "normal"))):
        text(ax, 9.55, 9.88 - 0.24 * i, line, size, weight, ha="left")
    fx, fy, fs = 13.35, 9.42, 0.92
    draw_fan(ax, fx, fy, fs)
    for dx, term in ((-0.2, "fan red"), (0.2, "fan black")):
        s_, colour = FLYING[term]
        lead_colour = "5V" if term == "fan red" else "GND"
        wire(ax, [(fx - fs / 2 + 0.05, fy - fs / 2 + 0.05), (fx + dx, 8.62)], lead_colour, lw=2.2, halo=2.0, z=4)
        marker(ax, fx + dx, 8.62, s_, colour)
        text(ax, fx + dx, 8.38, hole_name(landing(term)), 9, "bold", "#333333")
    for i, (line, size, weight) in enumerate((
            ("Fan, Orion OD4010-12HSS", 10, "bold"),
            ("Sits on its posts over this board, rotor up.", 9, "normal"),
            (f"Red lead (+) onto {hole_name(landing('fan red'))}, the 5V rail. Black", 9, "normal"),
            (f"lead (−) onto {hole_name(landing('fan black'))}, the drain: not GND.", 9, "normal"))):
        text(ax, 14.0, 9.88 - 0.24 * i, line, size, weight, ha="left")

    # --- legend ---------------------------------------------------------------------------------
    text(ax, 8.35, 3.3, "Nodes (BUILD.md):", 9.5, "bold", ha="left")
    x, renderer = 10.0, fig.canvas.get_renderer()
    for net, label in (("5V", "5V"), ("GND", "GND"), ("PWM", "PWM, D10"), ("GATE", "GATE"),
                       ("DRAIN", "DRAIN, fan −"), ("HALL", "HALL, D2")):
        t = chip(ax, x, 3.3, label, net, ha="left", size=9)
        x += t.get_window_extent(renderer=renderer).width / fig.dpi + 0.3

    # --- underside ------------------------------------------------------------------------------
    under = Board(ax, 1.2, 3.1, 0.24, nets, mirror=True)
    under.draw(size=8, row_labels=False)
    leaded = [part for part in PARTS if part[1] != "smd"]   # the chip is soldered on top only
    for h in [part[3][0] for part in leaded] + [part[4][0] for part in leaded] + [h for _, h in LANDINGS]:
        x, y = under.xy(h)
        ax.add_patch(Circle((x, y), 0.06, fc="#c9c9cc", ec="#555555", lw=0.6, zorder=5))
    for r in range(NROW):
        text(ax, 1.2 - 0.29, under.xy((0, r))[1], str(r + 1), 8, "bold", "#333333")
    text(ax, 0.3, 3.92, "Underneath, as you hold it to solder:", 9.5, "bold", ha="left")
    text(ax, 0.3, 3.7, "a mirror image, with column A on the right", 9, colour="#333333", ha="left")
    for i, line in enumerate(("Each coloured strip is a row of", "solder bridges, or a bare wire",
                              "soldered along the holes. Grey", "dots are leads from the top.")):
        text(ax, 3.55, 3.2 - 0.23 * i, line, 8.8, colour="#333333", ha="left")

    # --- notes ----------------------------------------------------------------------------------
    ax.add_patch(Rectangle((0.25, 0.15), W - 0.5, 1.3, fc="#f7f7f7", ec="#bbbbbb", lw=1.2, zorder=0))
    notes = (
        "The junction board is drawn from above as it sits in the base: the cable notch (−X) on the left, the MOSFET "
        "(+X) on the right. Rows 5 and 6 are the GND and 5V rails. It is the strip's full 20 mm width: "
        "its edges rest on the rails.\n"
        "Everything on top lies flat and under 3 mm, as the fan sits about 3.5 mm above the board. Leads are 4 holes "
        "apart (10.16 mm) for the resistors and 3 for the diode. C1 is a 1206 chip, soldered on top across E5 and E6.\n"
        "The colours are the six nodes, not your wire colours: write down which cable core is which JST pin. "
        "The diode's band faces the 5V rail; backwards, it shorts 5 V when the fan turns on.\n"
        "The 10 k from GATE to GND holds the fan off while D10 isn't driving it (cable unplugged, Uno resetting). "
        "Bench-check the board (BUILD.md stage 5) before plugging it into the Uno."
    )
    text(ax, 0.42, 0.8, notes, 10, colour="#222222", ha="left", linespacing=1.55)
    return fig


def save(fig, path):
    fig.savefig(path, dpi=200, facecolor="white")
    plt.close(fig)


def hole_list(nets):
    """The holes and bridges, by part and by node, as BUILD.md stage 5 lists them."""
    lines = ["parts and leads:"]
    for part in PARTS:
        lines.append(f"  {part[0]} {part[2]}: " + ", ".join(f"{hole_name(h)} ({t})" for h, t in (part[3], part[4])))
    for term, h in LANDINGS:
        lines.append(f"  {term}: {hole_name(h)}")
    lines.append("bridges:")
    for net in NETLIST:
        pairs = [f"{hole_name(u)}-{hole_name(v)}" for u, v in BRIDGES if nets[u] == net]
        lines.append(f"  {net}: " + ", ".join(pairs))
    return "\n".join(lines)


if __name__ == "__main__":
    nets = check()
    print("layout matches BUILD.md's netlist:", len(BRIDGES), "bridges")
    print(f"board: {NCOL} x {NROW} holes, {NCOL * PITCH:.2f} x {STRIP_W:.1f} mm")
    for name, (spare, post) in fit().items():
        print(f"  {name}: {spare:.2f} mm left at the -X wall, {post:.2f} mm from the fan posts")
    print(hole_list(nets))
    save(figure(nets), OUT)
    print("wrote", OUT)

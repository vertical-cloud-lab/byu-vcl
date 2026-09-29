"""Draw the Tic T500 <-> OT-2 P20 GEN2 wiring diagrams used in
cubos/docs/tic-t500-pipette-setup.md.

    python cubos/docs/_static/tic_t500_wiring.py

writes tic-t500-pipette-stepdir.png (Figure 1) and tic-t500-pipette-usb.png
(Figure 2) next to this script. Matplotlib only.

Sources for every pin and number drawn here are listed in the doc. In short:
Tic pin labels and edge order are Pololu's T500 pinout diagram (tic03b); the
pipette header layout is the science-jubilee photo already in this folder
(ot2-pipette-header-pinout.png, doc section 8.6 of opentrons-pipette-wiring.md).
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patheffects as pe  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle  # noqa: E402

HERE = Path(__file__).resolve().parent

W, H = 16.0, 8.6

C = {
    "red": "#d62728",  # coil A, header pin 3
    "blue": "#1f5fbf",  # coil A, header pin 4
    "green": "#1e8a3e",  # coil B, header pin 1
    "black": "#262626",  # coil B, header pin 2
    "tan": "#c29450",  # switch signal, header pin 7
    "purple": "#7b3fa0",  # switch return, header pin 6
    "step": "#1fa493",
    "dir": "#e0609f",
    "gnd": "#6b6b6b",
    "vplus": "#c00000",
    "vminus": "#111111",
    "usb": "#5b6b7b",
    "unused": "#dcdcdc",
    "muted": "#8a8a8a",
    "tic_body": "#f6d4d1",
    "tic_edge": "#b03a3a",
}

# --- pipette 10-pin header, laid out as in the science-jubilee photo -------
HDR_COLS = {"L": 12.55, "R": 13.30}
HDR_ROWS = {1: 1.75, 2: 2.45, 3: 3.15, 4: 3.85, 5: 4.55}  # row 1 = tip end
HDR_LAYOUT = {
    (1, "L"): 2, (1, "R"): 1,
    (2, "L"): 4, (2, "R"): 3,
    (3, "L"): 6, (3, "R"): 5,
    (4, "L"): 8, (4, "R"): 7,
    (5, "L"): 10, (5, "R"): 9,
}
HDR_COLOUR = {1: "green", 2: "black", 3: "red", 4: "blue", 6: "purple", 7: "tan"}
PIN_S = 0.46
GAP_X = (HDR_COLS["L"] + HDR_COLS["R"]) / 2  # channel between the columns

# --- Tic T500, top view (Pololu's pinout photo) -----------------------------
TIC = dict(x0=5.8, x1=10.2, y0=1.8, y1=5.4)
TIC_LEFT = ["ERR", "RST", "SCL", "SDA/AN", "GND", "TX", "RX", "RC", "5V (out)", "GND"]
TIC_LEFT_Y = {name: 5.0 - 0.32 * i for i, name in enumerate(TIC_LEFT)}
TIC_TOP = [("STEP", 7.50), ("DIR", 7.85), ("GND", 8.20), ("GND", 8.55), ("VM", 8.90)]
TIC_RIGHT = [("VIN", 4.7), ("GND", 4.2), ("A2", 3.6), ("A1", 3.1), ("B1", 2.6), ("B2", 2.1)]
TIC_RIGHT_Y = dict(TIC_RIGHT)


def hdr_pin(n):
    for (r, c), num in HDR_LAYOUT.items():
        if num == n:
            return HDR_COLS[c], HDR_ROWS[r]
    raise KeyError(n)


def wire(ax, pts, colour, lw=3.4, z=3):
    xs, ys = zip(*pts)
    ax.plot(
        xs, ys, color=C[colour] if colour in C else colour, lw=lw, zorder=z,
        solid_capstyle="round", solid_joinstyle="round",
        path_effects=[pe.Stroke(linewidth=lw + 4, foreground="white"), pe.Normal()],
    )


def draw_header(ax):
    x0, y0 = 12.05, 1.15
    ax.add_patch(FancyBboxPatch((x0, y0), 1.75, 4.0, boxstyle="round,pad=0,rounding_size=0.25",
                                fc="#b8b8b8", ec="#4d4d4d", lw=2, zorder=1))
    for (r, c), n in HDR_LAYOUT.items():
        cx, cy = HDR_COLS[c], HDR_ROWS[r]
        used = n in HDR_COLOUR
        fc = C[HDR_COLOUR[n]] if used else C["unused"]
        ax.add_patch(Rectangle((cx - PIN_S / 2, cy - PIN_S / 2), PIN_S, PIN_S, fc=fc,
                               ec="#333333", lw=1.6, zorder=6))
        tc = "white" if used and n != 7 else ("#222222" if n == 7 else "#666666")
        ax.text(cx, cy, str(n), ha="center", va="center", fontsize=16, fontweight="bold",
                color=tc, zorder=7)
    ax.text(13.1, 6.05, "OT-2 P20 GEN2", ha="center", va="center", fontsize=17,
            fontweight="bold")
    ax.text(13.1, 5.72, "pipette, 10-pin header", ha="center", va="center", fontsize=11,
            color="#222222")
    ax.text(13.1, 5.43, "bottom row is nearest the tip", ha="center", va="center", fontsize=9.5,
            color="#444444")
    notes = [
        (4.55, "5, 8–10: unused", C["muted"]),
        (3.85, "7: switch signal", "#333333"),
        (3.15, "6: switch return", "#333333"),
        (2.45, "3 + 4: coil A", "#333333"),
        (1.75, "1 + 2: coil B", "#333333"),
    ]
    for y, t, col in notes:
        ax.text(14.55, y, t, ha="left", va="center", fontsize=11, color=col)


def draw_tic(ax, used, centre_lines):
    """used: dict pin-key -> colour name, keys like ('L','SCL'), ('T',8.55), ('R','A1')."""
    x0, x1, y0, y1 = TIC["x0"], TIC["x1"], TIC["y0"], TIC["y1"]
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0,
                                boxstyle="round,pad=0,rounding_size=0.18",
                                fc=C["tic_body"], ec=C["tic_edge"], lw=2.2, zorder=1))
    # USB Micro-B on the top edge, left of the STEP/DIR header
    ax.add_patch(Rectangle((6.12, y1 - 0.14), 0.52, 0.30, fc="#c9c9c9", ec="#555555", lw=1.4,
                           zorder=5))
    ax.text(6.38, y1 + 0.01, "USB", ha="center", va="center", fontsize=8.5, color="#222222",
            fontweight="bold", zorder=6)

    def pin(x, y, key, label, ha, dx, dy=0.0, rot=0):
        col = used.get(key)
        ax.add_patch(Circle((x, y), 0.085, fc=C[col] if col else "white",
                            ec="#333333" if col else "#999999", lw=1.4, zorder=6))
        ax.text(x + dx, y + dy, label, ha=ha, va="center", fontsize=11.5, rotation=rot,
                color="#222222" if col else C["muted"],
                fontweight="bold" if col else "normal", zorder=6)

    for name in TIC_LEFT:
        pin(x0, TIC_LEFT_Y[name], ("L", name), name, "left", 0.17)
    for name, x in TIC_TOP:
        pin(x, y1, ("T", x), name, "center", 0.0, -0.36, rot=90)
    for name, y in TIC_RIGHT:
        pin(x1, y, ("R", name), name, "right", -0.17)

    cx = 8.2
    for i, (t, size, weight) in enumerate(centre_lines):
        ax.text(cx, 3.75 - 0.34 * i, t, ha="center", va="center", fontsize=size,
                fontweight=weight, color="#3a1010", zorder=6)
    ax.text(8.2, 1.5, "Pololu Tic T500 (#3134)", ha="center", va="center", fontsize=16,
            fontweight="bold")


def draw_psu(ax):
    ax.add_patch(Rectangle((8.95, 6.2), 2.15, 1.05, fc="white", ec="#222222", lw=2, zorder=4))
    ax.text(10.02, 6.93, "12 V DC supply", ha="center", va="center", fontsize=14,
            fontweight="bold", zorder=5)
    ax.text(10.02, 6.62, "≥ 2 A · T500 takes 4.5–35 V", ha="center", va="center", fontsize=9.5,
            zorder=5)
    for x, t in ((10.5, "+"), (10.85, "−")):
        ax.text(x, 6.36, t, ha="center", va="center", fontsize=13, fontweight="bold", zorder=5)
    # VIN (upper terminal pin) takes the inner vertical so the two never cross
    wire(ax, [(TIC["x1"], TIC_RIGHT_Y["VIN"]), (10.5, TIC_RIGHT_Y["VIN"]), (10.5, 6.2)], "vplus")
    wire(ax, [(TIC["x1"], TIC_RIGHT_Y["GND"]), (10.85, TIC_RIGHT_Y["GND"]), (10.85, 6.2)],
         "vminus")


def draw_coils(ax):
    """A1 red / A2 blue / B1 green / B2 black, i.e. the TMC2209's 1A/1B/2A/2B
    colours moved to the same-named Tic terminals.  One unavoidable crossing
    (black under green); green is drawn last so it reads as passing over."""
    xr = TIC["x1"]
    lx = HDR_COLS["L"] - PIN_S / 2  # left face of the left column
    rx = HDR_COLS["R"] - PIN_S / 2  # left face of the right column
    x4, y4 = hdr_pin(4)
    x3, y3 = hdr_pin(3)
    x2, y2 = hdr_pin(2)
    x1, y1 = hdr_pin(1)
    wire(ax, [(xr, TIC_RIGHT_Y["B2"]), (10.55, TIC_RIGHT_Y["B2"]), (10.55, y2), (lx, y2)], "black")
    wire(ax, [(xr, TIC_RIGHT_Y["A2"]), (11.6, TIC_RIGHT_Y["A2"]), (11.6, y4), (lx, y4)], "blue")
    wire(ax, [(xr, TIC_RIGHT_Y["A1"]), (11.25, TIC_RIGHT_Y["A1"]), (11.25, 2.1), (GAP_X, 2.1),
              (GAP_X, y3), (rx, y3)], "red")
    wire(ax, [(xr, TIC_RIGHT_Y["B1"]), (10.9, TIC_RIGHT_Y["B1"]), (10.9, 1.4), (GAP_X, 1.4),
              (GAP_X, y1), (rx, y1)], "green")


def switch_exits():
    """Start points of the two limit-switch wires at the header."""
    x7, y7 = hdr_pin(7)
    x6, y6 = hdr_pin(6)
    tan = [(x7 + PIN_S / 2, y7), (14.35, y7)]
    purple = [(x6 + PIN_S / 2, y6), (GAP_X, y6), (GAP_X, 4.97), (11.85, 4.97)]
    return tan, purple


def base_axes():
    fig = plt.figure(figsize=(W, H), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    return fig, ax


def figure_stepdir(path):
    fig, ax = base_axes()
    ax.text(0.3, 8.3, "Figure 1 — Tic T500 as a drop-in for the TMC2209: the Arduino keeps STEP/DIR "
            "and the limit switch", ha="left", va="center", fontsize=15, fontweight="bold")

    used = {("T", 7.50): "step", ("T", 7.85): "dir", ("T", 8.20): "gnd",
            ("R", "VIN"): "vplus", ("R", "GND"): "vminus",
            ("R", "A2"): "blue", ("R", "A1"): "red", ("R", "B1"): "green", ("R", "B2"): "black"}
    draw_tic(ax, used, [
        ("control mode:", 11, "normal"),
        ("STEP/DIR", 13, "bold"),
        ("step 1/8 · 990 mA", 11, "normal"),
        ("set over USB first", 10, "normal"),
        ("left-edge pins unused", 10, "normal"),
    ])
    draw_header(ax)
    draw_psu(ax)
    draw_coils(ax)

    # Arduino column
    sq_x = 3.35
    ax.text(1.95, 6.3, "Arduino Uno R3", ha="center", va="center", fontsize=19, fontweight="bold")
    ax.text(1.95, 5.98, "capper + pipette · USB-B to the Pi as now", ha="center", va="center",
            fontsize=10, color="#333333")
    rows = [
        (5.55, "D9  (limit switch)", "tan"),
        (5.00, "GND  (switch return)", "purple"),
        (4.30, "GND  (common ground)", "gnd"),
        (3.75, "A3  (DIR, D17)", "dir"),
        (3.20, "A2  (STEP, D16)", "step"),
        (2.45, "A0, A1  (old UART): unused", None),
        (1.95, "A4  (old EN): unused", None),
        (1.45, "5V: unused", None),
    ]
    for y, label, col in rows:
        ax.add_patch(Rectangle((sq_x, y - 0.21), 0.42, 0.42, fc=C[col] if col else C["unused"],
                               ec="#333333" if col else "#aaaaaa", lw=1.6, zorder=6))
        ax.text(sq_x - 0.14, y, label, ha="right", va="center", fontsize=12.5,
                color="#1a1a1a" if col else C["muted"], fontweight="bold" if col else "normal")
    ard_x = sq_x + 0.42

    # STEP / DIR / GND: leftmost start takes the lowest run and the lowest row
    y1 = TIC["y1"]
    wire(ax, [(7.50, y1), (7.50, 6.45), (5.40, 6.45), (5.40, 3.20), (ard_x, 3.20)], "step")
    wire(ax, [(7.85, y1), (7.85, 6.70), (5.15, 6.70), (5.15, 3.75), (ard_x, 3.75)], "dir")
    wire(ax, [(8.20, y1), (8.20, 6.95), (4.90, 6.95), (4.90, 4.30), (ard_x, 4.30)], "gnd")

    # limit switch: over the top to D9 and GND, unchanged from the TMC2209 build
    tan, purple = switch_exits()
    wire(ax, tan + [(14.35, 7.95), (4.20, 7.95), (4.20, 5.55), (ard_x, 5.55)], "tan")
    wire(ax, purple + [(11.85, 7.70), (4.45, 7.70), (4.45, 5.00), (ard_x, 5.00)], "purple")

    # notes
    ax.add_patch(Rectangle((0.25, 0.1), 15.5, 0.88, fc="#f7f7f7", ec="#bbbbbb", lw=1.2, zorder=0))
    notes = (
        "Motor: coil A = header pins 3 + 4 → A1 + A2; coil B = header pins 1 + 2 → B1 + B2. "
        "Swapping the two wires of ONE coil only reverses the direction of travel.\n"
        "Leave A0/A1 (and the 10 kΩ bridge), A4 and 5V unconnected. Never move the old EN wire "
        "to RST: the firmware holds A4 LOW, which would keep the Tic in reset.\n"
        "Firmware: STEPS_PER_MM 1592 → 796, because the T500 stops at 1/8 step. Rewire only with "
        "the 12 V off; Pololu warns that doing it live can destroy the driver."
    )
    ax.text(0.45, 0.54, notes, ha="left", va="center", fontsize=10.5, color="#222222",
            linespacing=1.5)
    fig.savefig(path, dpi=200, facecolor="white")
    plt.close(fig)


def figure_usb(path):
    fig, ax = base_axes()
    ax.text(0.3, 8.3, "Figure 2 — later option: the Tic runs the pipette by itself, commanded by "
            "the Pi over USB", ha="left", va="center", fontsize=15, fontweight="bold")

    used = {("L", "SCL"): "tan", ("T", 8.55): "purple",
            ("R", "VIN"): "vplus", ("R", "GND"): "vminus",
            ("R", "A2"): "blue", ("R", "A1"): "red", ("R", "B1"): "green", ("R", "B2"): "black"}
    draw_tic(ax, used, [
        ("control mode:", 11, "normal"),
        ("Serial / I²C / USB", 13, "bold"),
        ("step 1/8 · 990 mA", 11, "normal"),
        ("SCL = reverse limit", 10, "normal"),
        ("homes on its own", 10, "normal"),
    ])
    draw_header(ax)
    draw_psu(ax)
    draw_coils(ax)

    # Raspberry Pi, USB straight into the Tic
    ax.add_patch(FancyBboxPatch((0.4, 5.75), 3.5, 1.2, boxstyle="round,pad=0,rounding_size=0.12",
                                fc="#e7f0e7", ec="#3c6e3c", lw=2, zorder=4))
    ax.text(2.15, 6.55, "Raspberry Pi 5", ha="center", va="center", fontsize=17,
            fontweight="bold", zorder=5)
    ax.text(2.15, 6.15, "CubOS host · ticcmd / ticlib", ha="center", va="center", fontsize=10.5,
            zorder=5)
    wire(ax, [(3.9, 6.3), (6.38, 6.3), (6.38, TIC["y1"] + 0.16)], "usb", lw=5)
    ax.text(5.0, 6.52, "USB (native, no /dev/ttyACM)", ha="center", va="center", fontsize=10,
            color=C["usb"])

    # limit switch: signal under the Tic to SCL, return over the top to GND
    tan, purple = switch_exits()
    wire(ax, tan + [(14.35, 0.95), (5.35, 0.95), (5.35, TIC_LEFT_Y["SCL"]),
                    (TIC["x0"], TIC_LEFT_Y["SCL"])], "tan")
    wire(ax, purple + [(11.85, 7.70), (8.55, 7.70), (8.55, TIC["y1"])], "purple")

    settings = (
        "Tic settings (saved on the board)\n"
        "• control mode: Serial / I²C / USB\n"
        "• step mode 1/8 · current limit 990 mA\n"
        "• SCL: limit switch reverse,\n"
        "   Pull-up ✓  Active high ✓ (fail-safe NC)\n"
        "• homing speeds: towards / away\n"
        "• invert direction if + moves the plunger up\n"
        "• needs firmware ≥ 1.06 (limits, homing)\n"
        "\n"
        "The Arduino keeps the capper; its D9, A0–A4\n"
        "come free. CubOS needs a Tic pipette\n"
        "backend, which is not written yet."
    )
    ax.text(0.45, 3.2, settings, ha="left", va="center", fontsize=11, linespacing=1.5,
            color="#222222",
            bbox=dict(boxstyle="round,pad=0.45", fc="#f7f7f7", ec="#bbbbbb", lw=1.2))
    fig.savefig(path, dpi=200, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    figure_stepdir(HERE / "tic-t500-pipette-stepdir.png")
    figure_usb(HERE / "tic-t500-pipette-usb.png")
    print("wrote", HERE / "tic-t500-pipette-stepdir.png")
    print("wrote", HERE / "tic-t500-pipette-usb.png")

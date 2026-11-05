"""Round 8, scaling up (#303, PR #318): a large-format laser powder-bed printer and a robot DED cell for repairs, the
two machines the alloy route hands its alloy to once it has passed (Sterling's review: "add an EOS or some type of
large-format printer and show later on the printing of real aerospace parts and repairs of real ship parts").

* ``eos_m400``: EOS M 400-4, 4181 x 1613 x 2355 mm, about 4835 kg, a 400 x 400 x 400 mm build volume (the height
  includes the build plate), four 400 W Yb fibre lasers over the whole 400 x 400 mm field (EOS's data sheet and product
  page). Moving: the chamber door, the build plate going in, the recoater, the platform, the four beams, the build
  itself (pieces ``build0``.. in slabs here; ``scaleup.py`` cuts the parts' meshes at the layer height instead).
* ``meltio_cell``: Meltio Robot Cell, 4050 x 2350 x 3000 mm, an ABB six-axis robot and a two-axis positioner (8 axes),
  500 kg standard on the positioner, a print envelope of 1000 mm diameter x 1200 mm with the positioner interpolating
  and 2000 x 1000 x 1000 mm without it, with the Blue Laser Engine: 1000 W from nine 450 nm diodes, a robot-mounted
  head 262 x 272 x 572 mm, wire 0.8-1.2 mm (meltio3d.com's Robot Cell page). Moving: the two front doors, the
  positioner's tilt and turn, the robot's axes, the beads of a repair, the restored edge.

The parts are real ones with public figures, their shapes drawn from those figures (``SOURCES``):

* the Sentinel-1 antenna bracket of RUAG Space, Altair and EOS (EOS case study): AlSi10Mg, 40 cm long, printed by citim
  on an EOS M 400, two brackets with 30 tensile specimens in one build of about 80 h at 60 um layers. The shape here is
  schematic (a topology-optimized truss of our drawing, 380 x 110 x 100 mm), not RUAG's geometry, which isn't public.
* the WAAMpeller of RAMLAB, Damen, Promarin, Autodesk and Bureau Veritas: a three-bladed nickel aluminium bronze ship
  propeller, 1350 mm across, about 400 kg, after Promarin's design for Damen's Stan Tug 1606. The blade sections, chord,
  thickness, pitch and skew here are a standard-series estimate, not Promarin's design. The damage (a notch eroded into
  the leading edge at 0.70-0.88 R, 30 mm deep at most) and the repair's beads are illustrative.

Frame as in ``instruments.py``: x right, y away from you facing the front, z up, origin at the centre of the footprint,
mm. ``FLOOR_PLACEMENT`` puts both in ``setup_lab``'s floor frame. Robot sizes are estimates after ABB's IRB 2600
(Meltio's page names ABB, not the model); every other estimate is marked where it is made.
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq
import numpy as np
import pyvista as pv

import instruments as I
from instruments import Instrument, Joint, _piece, _xcyl, _ycyl
from instruments_lab import Timeline, Turn

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lab_models"))
from common import box, cyl  # noqa: E402

# ===================================================================================================== sources
SOURCES = {
    "eos_m400": [
        "EOS M 400-4 product page and system data sheet (eos.info/en/industrial-3d-printer/metal/eos-m-400-4; "
        "eos.info/en-us/metal-solutions/metal-printers/data-sheets/sds-eos-m-400-4): build volume 400 x 400 x 400 mm "
        "including the build plate; 4 x 400 W Yb fibre lasers, 4 F-theta lenses and 4 scanners, each over the whole "
        "400 x 400 mm field; up to 7.0 m/s; focus about 90 um; 3 x 50 A; 45 kW maximum, 22 kW typical; compressed air "
        "7 bar, 20 m3/h; system 4181 x 1613 x 2355 mm, about 4835 kg; installation space at least 6500 x 6000 x 3300 mm",
        "Look (approximate, from EOS's product photos): the process station on the left, its chamber door with a large "
        "window at working height, the optics housing on top; the setup and unpacking station on the right with glove "
        "ports under a window; a touchscreen on an arm. The chamber's insides (dispenser, recoater, the four scanners' "
        "positions) are drawn schematically",
    ],
    "meltio_cell": [
        "Meltio Robot Cell (meltio3d.com/metal-3d-printers/meltio-robot-cell): 4050 x 2350 x 3000 mm; 8 axes, ABB robot "
        "with SafeMove; 2-axis positioner, 500 kg standard; print envelope 1000 mm diameter x 1200 mm with positioner "
        "interpolation, 2000 x 1000 x 1000 mm without; 300 x 400 mm actively cooled build plate (150 x 200 and 120 x "
        "100 also); Class 1 enclosure with interlocks and active laser windows; three 50 L argon bottles; external "
        "feeders for spools and drums over 100 kg; 400 V 3-phase, 20 kW peak, 7 kW average",
        "Blue Laser Engine Integration Kit (same page): 1000 W from 9 x 450 nm direct diode lasers; robot-mounted "
        "printhead 262 x 272 x 572 mm, 20.5-23 kg, water-cooled; control unit 600 x 300 x 800 mm, wall-mounted; wire "
        "0.8-1.2 mm, single or dual; materials listed: stainless, carbon and tool steels, nickel alloys, titanium, "
        "copper alloys (nickel aluminium bronze is not named). 2025 data sheet as indexed: 4000 kg (not on the page)",
        "Robot drawn after ABB's IRB 2600 (an estimate: Meltio names ABB but not the model): shoulder 445 mm up, 150 mm "
        "forward, lower arm 700 mm, upper arm to the wrist 795 mm; on a 550 mm riser. Positioner drawn as a tilt-and-"
        "turn unit, tilt axis 800 mm up (an estimate). The doors, posts and panels are our reading of Meltio's photos",
    ],
    "bracket": [
        "EOS case study, RUAG Space (uk.eos.info/.../cs_m_aerospace_ruag_en.pdf): Sentinel-1 antenna bracket, "
        "redesigned with Altair, printed by citim GmbH on an EOS M 400 in EOS Aluminium AlSi10Mg, 60 um layers; one "
        "build held two antenna brackets, 30 tensile specimens and other test items, in about 80 h; 40 cm long; "
        "stiffness more than 30 % over its minimum; qualified and approved for flight. Weight saving: 40 % in the case "
        "study; 1.6 kg original and 1.2 kg after the first loop in RUAG's Altair talk (speakerdeck.com/altairhyperworks)",
    ],
    "propeller": [
        "MarineLink, '3D Printed Ship's Propeller Prototype Produced' (marinelink.com/amp/news/propeller-prototype429251):"
        " the WAAMpeller, by Damen Shipyards, RAMLAB, Promarin, Autodesk and Bureau Veritas, 1350 mm diameter, about "
        "400 kg, nickel aluminium bronze, wire arc additive manufacturing on a Valk Welding system at RAMLAB, Port of "
        "Rotterdam; triple-blade, after Promarin's design for Damen's Stan Tug 1606; CNC milled afterwards",
        "Blade geometry here: chord, thickness, pitch ratio 0.9, skew 15 deg at the tip and NACA-like sections are a "
        "standard-series estimate, not Promarin's design (which is not public)",
    ],
}

# Navy context, for the chapter's captions: AML3D's ARCEMY WAAM systems print copper-nickel and nickel aluminium bronze
# parts for the US Navy's submarine industrial base (metal-am.com, 2023: a NAB prototype of about a tonne; Austal USA's
# CuNi production order, defenceconnect.com.au). Kept as context: the ARCEMY's outer size isn't published.
NAVY = ("AML3D's ARCEMY wire-arc cells print copper-nickel and nickel aluminium bronze parts for the US Navy's "
        "submarine industrial base (metal-am.com; defenceconnect.com.au)")

# key -> (W, D, H mm, mass kg, product, source URL, "floor"), as instruments_r7.FOOTPRINTS
FOOTPRINTS = {
    "eos_m400": (4181.0, 1613.0, 2355.0, 4835.0, "EOS M 400-4, 4 x 400 W, 400 x 400 x 400 mm",
                 "https://eos.info/en/industrial-3d-printer/metal/eos-m-400-4", "floor"),
    "meltio_cell": (4050.0, 2350.0, 3000.0, 4000.0, "Meltio Robot Cell with the Blue Laser Engine (1000 W, 450 nm); "
                    "mass from the 2025 data sheet as indexed", "https://meltio3d.com/metal-3d-printers/meltio-robot-cell",
                    "floor"),
}

# What size of part each machine in the route can take (published figures; notes/scaleup.md)
ENVELOPES = {
    "InssTek MX-Lab (DED, in the lab)": "150 x 150 x 150 mm stroke on a 175 x 175 mm table",
    "Aconity MIDI (LPBF, in the lab)": "170 mm diameter x 200 mm",
    "EOS M 400-4 (LPBF)": "400 x 400 x 400 mm, the plate included",
    "Meltio Robot Cell (DED)": "1000 mm dia. x 1200 mm with the positioner turning; 2000 x 1000 x 1000 mm robot only; "
                               "500 kg",
}

# ===================================================================================================== the floor
# setup_lab's floor frame (warehouse.py): the main aisle along x from -10200 to 10200 between y -2400 and -5400; the
# south row's fronts on y = -6238; pallet racking along both side walls (x beyond +-11833) from y = -9200 north, and
# along the back. Neither machine fits in a row: 4.2 m and 4.05 m wide where the free gaps are 4.17 m (east of the
# wire EDM, beside the racking and over its MiR pivot spot) and 4.65 m (west of the Instron 68FM-100, in front of the
# racking), and EOS asks for at least 6.5 x 6.0 m to install the M 400-4. So they stand south of the south row, past the
# racking's ends, fronts to the north, each with a 2.4 m or wider clear strip in front of it running up to the aisle's
# end. No MiR dock: the powder comes by the 100 kg in EOS's containers and a propeller (400 kg) by forklift or crane.
# x, y: the centre of the footprint; turn: degrees about z, counterclockwise from above; 0 = front to -y (the north
# row's way), 180 = front to +y.
FLOOR_PLACEMENT = {
    "eos_m400": dict(x=-9600.0, y=-10300.0, turn=180.0),       # x -11691..-7510, y -11107..-9494
    "meltio_cell": dict(x=9700.0, y=-10600.0, turn=180.0),     # x 7675..11725, y -11775..-9425
}
FLOOR_RECTS = {      # setup_lab fit's rectangles (out/tray_plan.json, 2026-11-04) and the racking, for check_floor()
    "instron_floor": (-7187, -5613, -7034, -6238), "instron_small": (-4540, -4060, -6873, -6238),
    "fumehood": (890, 2110, -7197, -6238), "ded": (3238, 4561, -7015, -6238), "wire_edm": (5540, 7660, -8782, -6238),
    "charger0": (-1811, -1189, -6725, -6238), "charger1": (-611, 11, -6725, -6238),
    "racking west": (-12900, -11833, -9200, 4515), "racking east": (11833, 12900, -9200, 4515),
    "aisle": (-10200, 10200, -5400, -2400),
}


def check_floor() -> dict:
    """Each placement's rectangle against FLOOR_RECTS: the least gap in mm (negative = overlap)."""
    out = {}
    for key, p in FLOOR_PLACEMENT.items():
        w, d = FOOTPRINTS[key][:2]
        if abs(p["turn"]) % 180 > 1:
            w, d = d, w
        r = (p["x"] - w / 2, p["x"] + w / 2, p["y"] - d / 2, p["y"] + d / 2)
        gaps = {}
        for k, (x0, x1, y0, y1) in FLOOR_RECTS.items():
            gx = max(x0 - r[1], r[0] - x1)
            gy = max(y0 - r[3], r[2] - y1)
            gaps[k] = round(max(gx, gy) if (gx > 0 or gy > 0) else max(gx, gy))
        out[key] = dict(rect=[round(v) for v in r], least_gap=min(gaps.values()),
                        nearest=min(gaps, key=gaps.get))
    return out


# ===================================================================================================== materials
MATERIALS = {
    "r8s_eos_white": (0.93, 0.93, 0.92, 1.0, 0.25),
    "r8s_eos_grey": (0.55, 0.57, 0.60, 1.0, 0.30),
    "r8s_eos_dark": (0.20, 0.21, 0.23, 1.0, 0.30),
    "r8s_eos_blue": (0.00, 0.33, 0.62, 1.0, 0.30),
    "r8s_window": (0.25, 0.55, 0.30, 0.32, 0.9),           # laser glazing, green tint (fibre lasers, 1070 nm)
    "r8s_amber": (0.95, 0.55, 0.12, 0.30, 0.9),            # blue-laser glazing (450 nm), amber
    "r8s_meltio": (0.16, 0.17, 0.19, 1.0, 0.30),
    "r8s_panel": (0.86, 0.87, 0.88, 1.0, 0.25),
    "r8s_abb": (0.93, 0.93, 0.91, 1.0, 0.30),             # ABB's robot white
    "r8s_abb_dk": (0.28, 0.29, 0.31, 1.0, 0.35),
    "r8s_orange": (0.95, 0.47, 0.10, 1.0, 0.30),
    "r8s_argon": (0.20, 0.45, 0.25, 1.0, 0.40),            # argon bottle green (estimate of the colour code)
    "r8s_powder": (0.55, 0.56, 0.58, 0.30, 0.05),          # the powder cake, drawn see-through
    "r8s_alsi": (0.80, 0.81, 0.83, 1.0, 0.55),             # AlSi10Mg as built
    "r8s_plate": (0.62, 0.63, 0.66, 1.0, 0.60),
    "r8s_nab": (0.78, 0.60, 0.36, 1.0, 0.55),              # nickel aluminium bronze, machined
    "r8s_bead": (0.50, 0.34, 0.20, 1.0, 0.30),             # as deposited: oxide-tinted, darker than machined
    "r8s_glow": (1.00, 0.55, 0.12, 1.0, 0.10),
    "r8s_blue": (0.25, 0.45, 1.00, 0.80, 0.0),             # the 450 nm beam
    "r8s_ir": (0.95, 0.10, 0.08, 0.85, 0.0),               # the fibre lasers' beams (invisible in life)
}
NAB_C = MATERIALS["r8s_nab"][:3]
ALSI_C = MATERIALS["r8s_alsi"][:3]
BEAD_C = MATERIALS["r8s_bead"][:3]


# ===================================================================================================== joints
@dataclass
class Reveal(Joint):
    """A piece that is there only while on <= v < off (a bead once it is laid, until the edge is machined back):
    shrunk to nothing about `centre` otherwise, so it never shows anywhere else."""
    on: float = 0.0
    off: float = 9.0
    centre: tuple = (0.0, 0.0, 0.0)
    kind: str = "reveal"

    def matrix(self, v: float) -> np.ndarray:
        if self.on <= v < self.off:
            return np.eye(4)
        c = np.asarray(self.centre, float)
        return I._T(c) @ np.diag([1e-4, 1e-4, 1e-4, 1.0]) @ I._T(-c)


# ===================================================================================================== mesh helpers
def _tube(pts, r, sides=14) -> pv.PolyData:
    pts = np.asarray(pts, float)
    line = pv.Spline(pts, max(len(pts) * 6, 24)) if len(pts) > 2 else pv.Line(pts[0], pts[1], resolution=4)
    return line.tube(radius=r, n_sides=sides, capping=True).triangulate()


def _merge(ms) -> pv.PolyData:
    ms = [m for m in ms if m is not None and m.n_points]
    out = ms[0].merge(ms[1:]) if len(ms) > 1 else ms[0]
    return out.clean().triangulate()


def _pbox(x0, y0, z0, x1, y1, z1) -> pv.PolyData:
    return pv.Box(bounds=(x0, x1, y0, y1, z0, z1)).triangulate()


# ===================================================================================================== the bracket
BRACKET = dict(L=380.0, W=110.0, H=100.0, pad=(64.0, 96.0, 12.0), ring_d=56.0, ring_h=26.0)


def bracket_mesh(at=(0.0, 0.0, 0.0)) -> pv.PolyData:
    """A topology-optimized antenna bracket after RUAG Space's Sentinel-1 bracket: two foot pads, an interface ring on
    top, and branching struts between them. Our drawing, 380 x 110 x 100 mm, lying on its feet as it would be built."""
    p = BRACKET
    L, W, H = p["L"], p["W"], p["H"]
    pw, pd, pt = p["pad"]
    ms = []
    for sx in (-1, 1):                                     # the two foot pads, each with two bolt bosses
        x = sx * (L / 2 - pw / 2)
        ms.append(_pbox(x - pw / 2, -pd / 2, 0, x + pw / 2, pd / 2, pt))
        for sy in (-1, 1):
            ms.append(pv.Cylinder(center=(x, sy * 28, pt + 4), direction=(0, 0, 1), radius=11, height=8,
                                  resolution=20).triangulate())
    rx, rz = 0.0, H - p["ring_h"] / 2                       # the interface ring, open in the middle
    ring = pv.Disc(center=(0, 0, 0), inner=p["ring_d"] / 2 - 12, outer=p["ring_d"] / 2, c_res=36)
    ms.append(ring.extrude((0, 0, p["ring_h"]), capping=True).translate((rx, 0, H - p["ring_h"]), inplace=False)
              .triangulate())
    top = np.array([0.0, 0.0, rz])
    for sx in (-1, 1):                                     # main struts: pad corners to the ring, bowed outwards
        x0 = sx * (L / 2 - pw / 2)
        for sy in (-1, 1):
            a = np.array([x0 + sx * 18, sy * 36, pt])
            b = np.array([sx * 30, sy * 22, rz - 6])
            mid = (a + b) / 2 + np.array([0, sy * 16, 22])
            ms.append(_tube([a, mid, b], 8.5))
        # a lower chord along each side and a diagonal brace
        for sy in (-1, 1):
            a = np.array([x0, sy * 40, pt + 4])
            m = np.array([sx * 70, sy * 48, 34])
            b = np.array([0, sy * 30, 44])
            ms.append(_tube([a, m, b], 6.0))
            ms.append(_tube([np.array([sx * 70, sy * 48, 34]), np.array([sx * 60, sy * 20, 70]), top - (0, 0, 8)], 5.0))
    ms.append(_tube([[0, -30, 44], [0, 0, 36], [0, 30, 44]], 6.0))   # the cross-tie under the ring
    ms.append(_tube([[0, -30, 44], [0, -20, 70], [0, -18, rz - 8]], 5.5))
    ms.append(_tube([[0, 30, 44], [0, 20, 70], [0, 18, rz - 8]], 5.5))
    return _merge(ms).translate(at, inplace=False)


def tensile_bars(z0: float, cx: float, cy: float, n_row=15, pitch=24.0, rows=(-170.0, 170.0), d=10.0, h=62.0):
    """30 round tensile blanks standing up, two rows of 15 along the plate's front and back edges (layout ours;
    the case study gives the count, not the layout or size)."""
    ms = []
    for ry in rows:
        for i in range(n_row):
            x = cx + (i - (n_row - 1) / 2) * pitch
            ms.append(pv.Cylinder(center=(x, cy + ry, z0 + h / 2), direction=(0, 0, 1), radius=d / 2, height=h,
                                  resolution=16).triangulate())
    return _merge(ms)


# ===================================================================================================== the propeller
PROP = dict(D=1350.0, Z=3, hub_d=250.0, hub_l=270.0, P_D=0.9, skew_tip=15.0, root_x=0.16,
            # x = r/R: chord/D and max thickness/D (standard-series estimates)
            xs=(0.16, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.88, 0.94, 0.98, 1.00),
            cD=(0.20, 0.215, 0.255, 0.285, 0.305, 0.315, 0.305, 0.275, 0.235, 0.185, 0.12, 0.05),
            tD=(0.046, 0.042, 0.035, 0.028, 0.022, 0.017, 0.013, 0.0095, 0.0072, 0.0058, 0.0048, 0.004),
            dmg=(0.70, 0.88, 30.0))      # the damage: from x 0.70 to 0.88, at most 30 mm deep into the leading edge


def _interp(x, key):
    return float(np.interp(x, PROP["xs"], PROP[key]))


def _section_xy(x: float, s: np.ndarray):
    """Chordwise s (0 at the leading edge, 1 at the trailing edge) -> (xi, eta_upper, eta_lower) in mm, the chord
    centred on the blade's reference line, xi towards the leading edge."""
    D = PROP["D"]
    c, t = _interp(x, "cD") * D, _interp(x, "tD") * D
    yt = 5 * (t / c) * (0.2969 * np.sqrt(s) - 0.1260 * s - 0.3516 * s ** 2 + 0.2843 * s ** 3 - 0.1036 * s ** 4) * c
    m = 0.018 * c                                                    # a light camber (estimate)
    yc = 4 * m * s * (1 - s)
    xi = (0.5 - s) * c
    return xi, yc + yt, yc - yt


def _wrap(x: float, xi, eta) -> np.ndarray:
    """Section coordinates at r = x R -> 3D points of blade 0 (pointing +x), on the helix of pitch P_D x D, with the
    skew. The axis is z; the blade's mid-plane at z = 0."""
    R = PROP["D"] / 2
    r = x * R
    phi = math.atan(PROP["P_D"] / (math.pi * x))
    skew = math.radians(PROP["skew_tip"]) * ((x - 0.2) / 0.8) ** 2 if x > 0.2 else 0.0
    arc = xi * math.cos(phi) - eta * math.sin(phi)
    ax = xi * math.sin(phi) + eta * math.cos(phi)
    th = arc / r + skew
    return np.stack([r * np.cos(th), r * np.sin(th), ax], axis=-1)


def dmg_depth(x) -> np.ndarray:
    x0, x1, dmax = PROP["dmg"]
    u = np.clip((np.asarray(x, float) - x0) / (x1 - x0), 0.0, 1.0)
    return dmax * np.sin(np.pi * u) ** 0.8


def _blade_grid(xs, s_lo, s_hi, n=44) -> pv.PolyData:
    """A closed loop of each section from s_lo(x) to s_hi(x) (upper side, then lower), lofted along xs."""
    rows = []
    for x, a, b in zip(xs, s_lo, s_hi):
        u = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, n))
        s = a + (b - a) * u
        xi, up, lo = _section_xy(x, s)
        loop_xi = np.concatenate([xi[::-1], xi[1:]])
        loop_eta = np.concatenate([up[::-1], lo[1:]])
        rows.append(_wrap(x, loop_xi, loop_eta))
    P = np.array(rows)                                  # (sections, points, 3)
    P = np.concatenate([P, P[:, :1]], axis=1)           # close each loop
    grid = pv.StructuredGrid(P[..., 0].T, P[..., 1].T, P[..., 2].T)
    surf = grid.extract_surface().triangulate()
    # cap the tip
    tip = P[-1, :-1]
    cap = pv.PolyData(np.vstack([tip, tip.mean(0)]),
                      faces=np.hstack([[3, i, (i + 1) % len(tip), len(tip)] for i in range(len(tip))]))
    return _merge([surf, cap])


def blade_meshes(damaged: bool):
    """(blade, patch): blade 0 with its leading edge cut back by the damage (or whole), and the patch that restores it
    (None when whole). In the propeller's frame."""
    x0, x1, _ = PROP["dmg"]
    xs = np.concatenate([np.linspace(PROP["root_x"], x0, 8), np.linspace(x0, x1, 22)[1:],
                         np.linspace(x1, 1.0, 12)[1:]])
    D = PROP["D"]
    cut = np.array([dmg_depth(x) / (_interp(x, "cD") * D) for x in xs]) if damaged else np.zeros(len(xs))
    blade = _blade_grid(xs, cut, np.ones(len(xs)))
    if not damaged:
        return blade, None
    band = np.linspace(x0, x1, 22)
    cb = np.array([dmg_depth(x) / (_interp(x, "cD") * D) for x in band])
    patch = _blade_grid(band, np.zeros(len(band)), np.maximum(cb, 1e-4), n=14)
    return blade, patch


def propeller_meshes(damaged=True) -> dict:
    """{name: PolyData} of the propeller in its own frame: axis z, hub from z = -hub_l/2 to hub_l/2, blade 0 along +x
    (damaged if asked), blades 1 and 2 at 120 and 240 deg."""
    blade0, patch = blade_meshes(damaged)
    whole, _ = blade_meshes(False)
    blades = [blade0] + [whole.rotate_z(120.0 * k, inplace=False) for k in (1, 2)]
    hub = pv.Cylinder(center=(0, 0, 0), direction=(0, 0, 1), radius=PROP["hub_d"] / 2, height=PROP["hub_l"],
                      resolution=48).triangulate()
    boss = pv.Cylinder(center=(0, 0, -PROP["hub_l"] / 2 - 40), direction=(0, 0, 1), radius=PROP["hub_d"] / 2 - 40,
                       height=80, resolution=48).triangulate()       # the boss cap, aft
    bore = pv.Cylinder(center=(0, 0, PROP["hub_l"] / 2 + 1), direction=(0, 0, 1), radius=55, height=2,
                       resolution=32).triangulate()
    out = dict(blades=_merge(blades + [hub, boss]), bore=bore)
    if patch is not None:
        out["patch"] = patch
    return out


def bead_paths(n_beads=6, w=5.5):
    """The repair's beads, in the propeller's frame: each a pass along the span over the cut face, layer j standing
    (j + 0.5) w out from it towards the original leading edge, where the notch is still that deep (plus half a bead
    of overbuild). [(points (k x 3), radius)], passes alternating in direction."""
    x0, x1, dmax = PROP["dmg"]
    D = PROP["D"]
    out = []
    for j in range(n_beads):
        off = (j + 0.5) * w
        xs = np.linspace(x0, x1, 60)
        dd = dmg_depth(xs)
        ok = dd + 0.5 * w > off
        if ok.sum() < 3:
            break
        pts, rad = [], []
        for x in xs[ok]:
            c = _interp(x, "cD") * D
            s = max((dmg_depth(x) - off) / c, 0.0)
            xi, up, lo = _section_xy(x, np.array([s]))
            pts.append(_wrap(x, xi, (up + lo) / 2)[0])
            rad.append(max(3.2, 0.62 * float(up[0] - lo[0])))
        pts = np.array(pts)
        if j % 2:
            pts = pts[::-1]
        out.append((pts, float(np.mean(rad))))
    return out


# ===================================================================================================== EOS M 400-4
EOS = dict(W=4181.0, D=1613.0, H=2355.0, plinth=90.0, split=2300.0, body_h=2050.0, P=1020.0, well=400.0,
           plate_t=30.0, Hb=100.0, ch_w=1000.0, ch_d=980.0, ch_z0=930.0, ch_z1=1760.0, n_slabs=5)


def eos_geometry() -> dict:
    """Where things are in the EOS model, for the chapter."""
    p = EOS
    W, D = p["W"], p["D"]
    xs = -W / 2 + p["split"]
    cx = (-W / 2 + xs) / 2 + 60.0
    cy = -D / 2 + 520.0
    return dict(xs=xs, cx=cx, cy=cy, P=p["P"], Hb=p["Hb"], ceiling=p["ch_z1"],
                scanners=[(cx + sx * 110, cy + sy * 110, p["ch_z1"] - 60) for sx in (-1, 1) for sy in (-1, 1)])


def eos_build_parts(g=None) -> dict:
    """The build in the model frame, the plate's top at P (the platform up): {name: (mesh, rgb)}."""
    g = g or eos_geometry()
    cx, cy, P = g["cx"], g["cy"], g["P"]
    br = [bracket_mesh((cx, cy + sy * 68.0, P)) for sy in (-1, 1)]
    bars = tensile_bars(P, cx, cy)
    return {"brackets": (_merge(br), ALSI_C), "bars": (bars, ALSI_C)}


def eos_m400() -> Instrument:
    p = EOS
    W, D, H = p["W"], p["D"], p["H"]
    g = eos_geometry()
    xs, cx, cy, P = g["xs"], g["cx"], g["cy"], g["P"]
    n = p["n_slabs"]
    inst = Instrument("eos_m400", "Large-format metal printer (LPBF), 4 lasers", "EOS M 400-4", (W, D, H),
                      "EOS M 400-4 data sheet and product page (4181 x 1613 x 2355 mm, about 4835 kg; 400 x 400 x "
                      "400 mm build incl. plate; 4 x 400 W fibre lasers); look approximate, from EOS's photos",
                      floor=True, props=("load", "powder", *(f"build{k}" for k in range(n))))
    yf = -D / 2
    yb = yf + 30.0
    body = _piece(inst, "body")
    body.add("plinth", box(-W / 2 + 30, yb + 30, 0, W / 2 - 30, D / 2 - 30, p["plinth"]), "r8s_eos_dark")
    # the process station: a housing with the chamber cut out of it, the optics housing on top
    c0x, c1x = cx - p["ch_w"] / 2, cx + p["ch_w"] / 2
    shell = box(-W / 2, yb, p["plinth"], xs - 10, D / 2, p["body_h"]).edges("|Y").fillet(16)
    shell = shell.cut(box(c0x, yb - 1, p["ch_z0"], c1x, yb + p["ch_d"], p["ch_z1"]))
    body.add("process station", shell, "r8s_eos_white")
    body.add("lower band", box(-W / 2 + 4, yb - 2, p["plinth"] + 20, xs - 14, yb, 620), "r8s_eos_grey")
    body.add("optics housing", box(-W / 2 + 260, yb + 260, p["body_h"], xs - 260, D / 2 - 80, H).edges("|Z")
             .fillet(30), "r8s_eos_white")
    body.add("optics band", box(-W / 2 + 258, yb + 258, H - 60, xs - 258, D / 2 - 78, H - 40), "r8s_eos_dark")
    body.add("logo", box(-W / 2 + 120, yb - 3, p["body_h"] - 150, -W / 2 + 420, yb, p["body_h"] - 80), "r8s_eos_blue")
    body.add("filter module", box(-W / 2 + 60, yb - 2, 700, -W / 2 + 600, yb, 880), "r8s_eos_dark")
    # the setup and unpacking station: a glovebox front, two glove ports, a window, a lower hatch
    body.add("setup station", box(xs + 10, yb, p["plinth"], W / 2, D / 2, p["body_h"] - 100).edges("|Y").fillet(16),
             "r8s_eos_white")
    body.add("setup window", box(xs + 240, yb - 8, 1180, W / 2 - 240, yb + 2, 1880), "r8s_window")
    body.add("setup frame", box(xs + 200, yb - 6, 1140, W / 2 - 200, yb, 1920).cut(
        box(xs + 240, yb - 7, 1180, W / 2 - 240, yb + 1, 1880)), "r8s_eos_dark")
    for k, gx in enumerate((xs + 640, W / 2 - 640)):
        body.add(f"glove port {k}", I._ycyl(230, 40, x=gx, y=yb - 40, z=1050).cut(
            I._ycyl(190, 42, x=gx, y=yb - 41, z=1050)), "r8s_eos_dark")
        body.add(f"glove {k}", I._ycyl(190, 6, x=gx, y=yb - 4, z=1050), "glove")
    body.add("lower hatch", box(xs + 200, yb - 4, 240, W / 2 - 200, yb, 760), "r8s_eos_grey")
    body.add("setup band", box(xs + 14, yb - 2, p["plinth"] + 20, W / 2 - 4, yb, 180), "r8s_eos_grey")
    body.add("e-stop", _ycyl(40, 18, x=c1x + 200, y=yb - 18, z=p["ch_z0"] - 120), "inst_red")
    body.add("screen arm", box(c1x + 120, yb - 120, 1580, c1x + 150, yb, 1610), "r8s_eos_dark")
    body.add("touchscreen", box(c1x + 40, yb - 160, 1380, c1x + 420, yb - 130, 1640), "screen_on")
    # the chamber: deck, the build well, the dosing slot, the four scanners in the ceiling
    deck = _piece(inst, "deck")
    half = p["well"] / 2
    dp = box(c0x + 10, yb + 10, P - 20, c1x - 10, yb + p["ch_d"] - 10, P).cut(
        box(cx - half, cy - half, P - 21, cx + half, cy + half, P + 1))
    dp = dp.cut(box(cx + half + 30, cy - half, P - 21, cx + half + 70, cy + half, P + 1))           # overflow
    deck.add("deck", dp, "stainless")
    deck.add("overflow", box(cx + half + 30, cy - half, P - 120, cx + half + 70, cy + half, P - 20), "inst_black")
    deck.add("build cylinder", box(cx - half - 16, cy - half - 16, P - 560, cx + half + 16, cy + half + 16, P - 20)
             .cut(box(cx - half, cy - half, P - 561, cx + half, cy + half, P - 19)), "steel")
    deck.add("dispenser", box(c0x + 20, cy - half - 20, P + 420, cx - half - 60, cy + half + 20, p["ch_z1"]),
             "r8s_eos_grey")
    deck.add("dispenser slot", box(cx - half - 112, cy - half - 10, P + 2, cx - half - 82, cy + half + 10, P + 420),
             "stainless")
    for k, (sx_, sy_, sz_) in enumerate(g["scanners"]):
        deck.add(f"scanner {k}", box(sx_ - 55, sy_ - 45, sz_, sx_ + 55, sy_ + 45, p["ch_z1"]), "inst_dark")
        deck.add(f"lens {k}", cyl(60, 4, x=sx_, y=sy_, z=sz_ - 4), "window")
    deck.add("chamber light", box(c0x + 40, yb + p["ch_d"] - 14, p["ch_z1"] - 50, c1x - 40, yb + p["ch_d"] - 10,
                                  p["ch_z1"] - 30), "vlm_led")
    # moving: platform (piston), the plate (load), the build (slabs on the plate), the cake, the recoater, the beams
    Hb, pt = p["Hb"], p["plate_t"]
    platform = _piece(inst, "platform")
    platform.add("piston", box(cx - half + 2, cy - half + 2, P - pt - 60, cx + half - 2, cy + half - 2, P - pt),
                 "steel")
    _piece(inst, "load").add("build plate", box(cx - half + 4, cy - half + 4, P - pt, cx + half - 4, cy + half - 4, P),
                             "r8s_plate")
    parts = eos_build_parts(g)
    edges = np.linspace(P, P + Hb, n + 1)
    for k in range(n):                                     # the build in n slabs, for the tour
        ms = []
        for mesh, col in parts.values():
            sl = mesh.clip_box((cx - 300, cx + 300, cy - 300, cy + 300, edges[k], edges[k + 1]), invert=False)
            if sl.n_points:
                ms.append(sl.extract_surface().triangulate())
        inst.meshes[f"build{k}"] = [(_merge(ms), ALSI_C, 1.0)]
    inst.meshes["cake"] = [(_pbox(cx - half + 4, cy - half + 4, P, cx + half - 4, cy + half - 4, P + Hb),
                            MATERIALS["r8s_powder"][:3], 0.30)]
    rec = _piece(inst, "recoater")
    rx0 = cx - half - 75
    rec.add("recoater carriage", box(rx0, cy - half - 50, P + 6, rx0 + 30, cy + half + 50, P + 70), "r8s_eos_grey")
    rec.add("recoater blade", box(rx0 + 10, cy - half - 6, P + 0.5, rx0 + 18, cy + half + 6, P + 8), "rubber")
    beams = _piece(inst, "beams")
    for k, (sx_, sy_, sz_) in enumerate(g["scanners"]):
        tx, ty = cx + (sx_ - cx) * 0.9, cy + (sy_ - cy) * 0.9
        beams.add(f"beam {k}", cq.Workplane().add(cq.Solid.makeCylinder(
            2.5, math.dist((sx_, sy_, sz_ - 4), (tx, ty, P)), cq.Vector(tx, ty, P),
            cq.Vector(sx_ - tx, sy_ - ty, sz_ - 4 - P).normalized())), "r8s_ir")
        beams.add(f"pool {k}", cyl(9, 1.5, x=tx, y=ty, z=P - 0.3), "r8s_glow")
    door = _piece(inst, "door")
    d0x, d1x, dz0, dz1 = c0x - 40, c1x + 40, p["ch_z0"] - 50, p["ch_z1"] + 50
    door.add("door", box(d0x, yb - 34, dz0, d1x, yb - 4, dz1).cut(box(d0x + 90, yb - 35, dz0 + 90, d1x - 90, yb - 3,
                                                                       dz1 - 90)), "r8s_eos_grey")
    door.add("door window", box(d0x + 90, yb - 24, dz0 + 90, d1x - 90, yb - 12, dz1 - 90), "r8s_window")
    door.add("door handle", box(d1x - 70, yb - 80, (dz0 + dz1) / 2 - 140, d1x - 50, yb - 34, (dz0 + dz1) / 2 + 140),
             "aluminium")
    joints = {
        "door": Joint("hinge", axis=(0, 0, 1), pivot=(d0x, yb - 34, 0), deg=-100.0),
        "platform": Joint("slide", vec=(0, 0, -Hb)),
        "load": Joint("path", parent="platform",
                      path=((0, -1300, 160), (0, -900, 120), (0, -420, 40), (0, 0, 30), (0, 0, 0))),
        "cake": Joint("fade", parent="load"),
        "recoater": Joint("slide", vec=(2 * half + 125, 0, 0)),
        "beams": Joint("fade"),
        **{f"build{k}": Joint("fade", parent="load") for k in range(n)},
    }
    inst.joints = joints
    acts = [("The EOS M 400-4: 4.2 m long and 4.8 t, a 400 x 400 x 400 mm build volume and four 400 W lasers, each "
             "reaching the whole field. The chamber door opens.", 2.0, {"door": (0.0, 1.0), "load": (0.0, 0.0)}),
            ("A 400 mm build plate goes onto the platform.", 2.0, {"load": (0.0, 1.0)}),
            ("Door shut, argon in. Drawn see-through from here.", 1.6,
             {"door": (1.0, 0.0), "~body": (0.0, 0.8), "~door": (0.0, 0.8)})]
    for k in range(n):
        acts.append(("The recoater spreads a layer from the dispenser; all four lasers melt it at once." if k == 0 else
                     "", 1.0, {"recoater": (0.0, 1.0) if k % 2 == 0 else (1.0, 0.0), "beams": (0.0, 0.0),
                               "platform": (None, k / n), "cake": (None, 1.0 if k else 0.0)}))
        acts.append(("Two antenna brackets after RUAG Space's Sentinel-1 bracket, and 30 tensile bars: the build "
                     "of EOS's case study, in AlSi10Mg (layers drawn 330x)." if k == 0 else "", 1.2,
                     {"beams": (1.0, 1.0), f"build{k}": (0.0, 1.0), "cake": (None, 1.0), "platform": (None, (k + 1) / n)}))
    acts.append(("Done: the platform lifts the plate out of the powder, and the door opens.", 2.4,
                 {"beams": (1.0, 0.0), "platform": (1.0, 0.0), "cake": (1.0, 0.0), "~body": (0.8, 0.0),
                  "~door": (0.8, 0.0)}))
    acts.append(("", 1.6, {"door": (0.0, 1.0)}))
    inst.actions = acts
    inst.labels = [("process chamber", (c0x + 60, yb - 34, p["ch_z1"] - 60), (0.14, 0.24)),
                   ("setup and unpacking station", (xs + 700, yb - 10, 1700), (0.82, 0.22)),
                   ("optics: 4 x 400 W", (cx, yb + 300, H), (0.40, 0.12))]
    inst.notes = ["4181 x 1613 x 2355 mm and about 4835 kg (EOS); installation space at least 6500 x 6000 x 3300 mm.",
                  "Needs 3 x 50 A (45 kW maximum), compressed air and argon: a floor machine, not a tray one."]
    inst.cam = (0.55, -2.0, 0.75)
    inst.framing = (0.9, 0.42)
    return inst


# ===================================================================================================== Meltio cell
CELL = dict(W=4050.0, D=2350.0, H=3000.0, post=80.0, door_w=950.0, door_h=2250.0, low=900.0,
            robot=(-430.0, 120.0), riser=550.0, sh_h=445.0, a1=150.0, L2=700.0, L3=795.0, wrist=85.0, head_l=572.0,
            stand=12.0, pos=(780.0, 120.0), tilt_z=800.0, face_off=150.0, face_d=650.0)


def _cell_k():
    c = CELL
    bx, by = c["robot"]
    zs = c["riser"] + c["sh_h"]
    Lt = c["wrist"] + c["head_l"] + c["stand"]
    return bx, by, zs, Lt


def robot_fk(q) -> dict:
    """Joint angles (deg: turret, shoulder, elbow, wrist pitch) -> the shoulder, elbow, wrist and tool tip points."""
    c = CELL
    bx, by, zs, Lt = _cell_k()
    t1, a, b, d = (math.radians(v) for v in q)
    u = np.array([math.cos(t1), math.sin(t1), 0.0])
    S = np.array([bx, by, zs]) + c["a1"] * u
    E = S + c["L2"] * (math.sin(a) * u + math.cos(a) * np.array([0, 0, 1.0]))
    Wc = E + c["L3"] * (math.cos(a + b) * u - math.sin(a + b) * np.array([0, 0, 1.0]))
    g = a + b + d
    tool = -math.sin(g) * u - math.cos(g) * np.array([0, 0, 1.0])
    return dict(S=S, E=E, W=Wc, tip=Wc + Lt * tool)


def robot_ik(p) -> tuple:
    """Tool tip at p, pointing straight down -> (turret, shoulder, elbow, wrist) in degrees, elbow up."""
    c = CELL
    bx, by, zs, Lt = _cell_k()
    w = np.asarray(p, float) + np.array([0, 0, Lt])
    t1 = math.atan2(w[1] - by, w[0] - bx)
    dr = math.hypot(w[0] - bx, w[1] - by) - c["a1"]
    dz = w[2] - zs
    L2, L3 = c["L2"], c["L3"]
    D2 = dr * dr + dz * dz
    cq_ = (D2 - L2 * L2 - L3 * L3) / (2 * L2 * L3)
    if abs(cq_) > 1.0:
        raise ValueError(f"out of reach: {math.sqrt(D2):.0f} mm from the shoulder")
    qrel = -math.acos(cq_)                                   # elbow up: the upper arm bends down from the lower
    a_abs = math.atan2(dz, dr) - math.atan2(L3 * math.sin(qrel), L2 + L3 * math.cos(qrel))
    alpha = math.pi / 2 - a_abs
    b_abs = a_abs + qrel
    beta = -b_abs - alpha
    delta = -(alpha + beta)
    return tuple(math.degrees(v) for v in (t1, alpha, beta, delta))


def prop_mount(tilt: float, spin: float = 0.0) -> np.ndarray:
    """The propeller's frame -> the cell's, at the positioner's tilt (deg, about x through the tilt axis) and turn."""
    c = CELL
    px, py = c["pos"]
    zt = c["tilt_z"]
    hub0 = zt + c["face_off"] + 40 + PROP["hub_l"] / 2           # the hub's centre over the faceplate, tilt 0
    M_spin = I._R((0, 0, 1), spin, (px, py, 0))
    M_tilt = I._R((1, 0, 0), tilt, (0, py, zt))
    M_seat = I._T((px, py, hub0)) @ I._R((0, 0, 1), 180.0)       # blade 0 to -x, towards the robot
    return M_tilt @ M_spin @ M_seat


def repair_tilt() -> float:
    """The positioner's tilt that turns the damaged leading edge at mid-span to face straight up."""
    x0, x1, _ = PROP["dmg"]
    xm = (x0 + x1) / 2
    D = PROP["D"]
    c = _interp(xm, "cD") * D
    s_cut = dmg_depth(xm) / c
    xi, up, lo = _section_xy(xm, np.array([s_cut, max(s_cut - 0.05, 0.0)]))
    pts = _wrap(xm, xi, (up + lo) / 2)
    d_loc = pts[1] - pts[0]                                       # towards the original leading edge
    best = None
    for t in np.arange(-120.0, 120.5, 0.5):
        M = prop_mount(t)
        d = M[:3, :3] @ d_loc
        z = d[2] / np.linalg.norm(d)
        if best is None or z > best[1]:
            best = (float(t), z)
    return best[0]


SAFE_Z = 1520.0          # the nozzle's height for swinging over the propeller (its top is about 1460 when tilted)


def repair_program(tilt=None):
    """The repair on one timeline: tilt the propeller, the robot from home down to the first bead, the beads (each in
    segments), lift, home; then the edge machined back. Returns (Timeline, beads [(segments, radius)], marks)."""
    tilt = repair_tilt() if tilt is None else tilt
    M = prop_mount(tilt)
    bx, by, _, _ = _cell_k()
    home = robot_ik((bx + 812 * math.cos(math.radians(150)), by + 812 * math.sin(math.radians(150)), SAFE_Z))
    tl = Timeline(dict(q=home, tilt=0.0, pool=0.0, built=frozenset()))
    tl.go(3.0, tilt=tilt).mark("tilted")
    beads = []
    for j, (pts, r) in enumerate(bead_paths()):
        k = len(pts)
        nseg = 6
        idx = np.linspace(0, k - 1, nseg + 1).round().astype(int)
        segs = [pts[idx[i]:idx[i + 1] + 1] for i in range(nseg)]
        beads.append((segs, r))
    above = None
    for j, (segs, r) in enumerate(beads):
        first = (M @ np.append(segs[0][0], 1.0))[:3] + (0, 0, r)
        if above is None:
            tl.go(2.5, q=robot_ik((first[0], first[1], SAFE_Z)))
            tl.go(1.5, q=robot_ik(first + (0, 0, 120)))
            tl.mark("approach")
        tl.go(0.6, q=robot_ik(first), pool=0.0)
        tl.go(0.3, pool=1.0)
        for i, seg in enumerate(segs):
            end = (M @ np.append(seg[-1], 1.0))[:3] + (0, 0, r)
            built = set(tl.states[-1]["built"]) | {(j, i)}
            tl.go(0.55, q=robot_ik(end), built=frozenset(built))
        tl.go(0.25, pool=0.0)
        above = end + (0, 0, 40)
        tl.go(0.3, q=robot_ik(above))
    tl.mark("deposited")
    tl.go(1.5, q=robot_ik((above[0], above[1], SAFE_Z)))
    tl.go(2.5, q=home).mark("home")
    tl.go(1.5).mark("machined")
    tl.go(2.5, tilt=0.0).mark("end")
    return tl, beads, tilt


def meltio_cell() -> Instrument:
    c = CELL
    W, D, H = c["W"], c["D"], c["H"]
    inst = Instrument("meltio_cell", "Robot DED cell for repairs (wire-laser, blue)", "Meltio Robot Cell", (W, D, H),
                      "Meltio Robot Cell (4050 x 2350 x 3000 mm; ABB robot + 2-axis positioner, 500 kg; 1000 mm dia. x "
                      "1200 mm envelope) with the Blue Laser Engine (1000 W, 9 x 450 nm); robot after ABB's IRB 2600 "
                      "(estimate); look from Meltio's photos", floor=True,
                      props=("prop", "patch", "glow", "beam", "bore"))
    yf, yb_ = -D / 2, D / 2
    post = c["post"]
    body = _piece(inst, "body")                       # the enclosure: posts, rails, panels, the roof
    for x in (-W / 2, -W / 2 + 1013, 0.0, W / 2 - 1013, W / 2):
        x0 = min(max(x - post / 2, -W / 2), W / 2 - post)
        for y0 in (yf, yb_ - post):
            body.add(f"post {x:.0f} {y0:.0f}", box(x0, y0, 0, x0 + post, y0 + post, H), "r8s_meltio")
    for y in (yf, yb_ - post):
        body.add(f"top rail {y:.0f}", box(-W / 2, y, H - 120, W / 2, y + post, H), "r8s_meltio")
        body.add(f"low rail {y:.0f}", box(-W / 2, y, c["low"] - 60, W / 2, y + post, c["low"]), "r8s_meltio")
    for x in (-W / 2, W / 2 - post):
        body.add(f"side top {x:.0f}", box(x, yf, H - 120, x + post, yb_, H), "r8s_meltio")
        body.add(f"side low {x:.0f}", box(x, yf, c["low"] - 60, x + post, yb_, c["low"]), "r8s_meltio")
        body.add(f"side panel {x:.0f}", box(x + 20, yf + post, 0, x + post - 20, yb_ - post, c["low"] - 60),
                 "r8s_panel")
        body.add(f"side window {x:.0f}", box(x + 30, yf + post, c["low"], x + post - 30, yb_ - post, H - 120),
                 "r8s_amber")
    body.add("back panel", box(-W / 2 + post, yb_ - post + 20, 0, W / 2 - post, yb_ - 20, c["low"] - 60), "r8s_panel")
    body.add("back window", box(-W / 2 + post, yb_ - post + 30, c["low"], W / 2 - post, yb_ - 30, H - 120),
             "r8s_amber")
    body.add("roof", box(-W / 2, yf, H - 20, W / 2, yb_, H), "r8s_panel")
    dw = c["door_w"]
    # the fixed front panels either side of the door opening, low panels and windows
    ox0, ox1 = -dw, dw
    for (a, b) in ((-W / 2 + post, ox0 - 40), (ox1 + 40, W / 2 - post)):
        body.add(f"front panel {a:.0f}", box(a, yf + 20, 0, b, yf + post - 20, c["low"] - 60), "r8s_panel")
        body.add(f"front window {a:.0f}", box(a, yf + 30, c["low"], b, yf + post - 30, H - 120), "r8s_amber")
    body.add("door header", box(ox0 - 40, yf, c["door_h"], ox1 + 40, yf + post, H - 120), "r8s_meltio")
    body.add("beacon", cyl(70, 160, x=W / 2 - 200, y=yf + 150, z=H), "r8s_orange")
    body.add("logo", box(-W / 2 + 200, yf - 3, H - 105, -W / 2 + 900, yf, H - 30), "inst_white")
    # outside: the control unit on the left wall, the HMI pedestal, argon bottles at the back, the wire drum
    body.add("control unit", box(-W / 2 - 300, -300, 900, -W / 2, 300, 1700), "r8s_meltio")
    body.add("control screen", box(-W / 2 - 304, -200, 1350, -W / 2 - 300, 200, 1600), "screen_on")
    body.add("hmi pedestal", box(-W / 2 + 420, yf - 420, 0, -W / 2 + 520, yf - 320, 1150), "r8s_meltio")
    body.add("hmi", box(-W / 2 + 300, yf - 440, 1150, -W / 2 + 640, yf - 400, 1450), "screen_on")
    for k in range(3):
        body.add(f"argon {k}", cyl(230, 1500, x=-W / 2 + 400 + 280 * k, y=yb_ + 160, z=0), "r8s_argon")
        body.add(f"argon cap {k}", cyl(90, 120, x=-W / 2 + 400 + 280 * k, y=yb_ + 160, z=1500), "chrome")
    body.add("wire drum", cyl(600, 820, x=W / 2 - 500, y=yb_ + 340, z=0), "r8s_meltio")
    body.add("drum top", cyl(560, 10, x=W / 2 - 500, y=yb_ + 340, z=820), "copper")
    # inside: the robot's riser and base, the positioner's base and side frames
    inner = _piece(inst, "inner")
    bx, by = c["robot"]
    inner.add("floor plate", box(-W / 2 + post, yf + post, 0, W / 2 - post, yb_ - post, 10), "r8s_eos_grey")
    inner.add("riser", box(bx - 300, by - 300, 10, bx + 300, by + 300, c["riser"]), "r8s_meltio")
    inner.add("robot base", cyl(520, 150, x=bx, y=by, z=c["riser"]), "r8s_abb")
    inner.add("cable", I._xcyl(60, 300, x=bx - 560, y=by + 200, z=200), "inst_black")
    px, py = c["pos"]
    zt = c["tilt_z"]
    inner.add("pedestal", box(px + 760, py - 260, 10, px + 960, py + 260, zt + 140), "r8s_orange")
    inner.add("pedestal foot", box(px + 700, py - 330, 10, px + 1020, py + 330, 80), "r8s_orange")
    inner.add("tilt bearing", _xcyl(300, 60, x=px + 700, y=py, z=zt), "r8s_abb_dk")
    inner.add("tilt motor", _xcyl(200, 180, x=px + 960, y=py, z=zt), "r8s_abb_dk")
    # the positioner's moving parts: the tilting cradle, the turning faceplate
    tiltp = _piece(inst, "tilt")
    tiltp.add("tilt shaft", _xcyl(190, 700, x=px, y=py, z=zt), "r8s_abb_dk")
    tiltp.add("cradle", box(px - 210, py - 210, zt - 110, px + 210, py + 210, zt + 80), "r8s_orange")
    tiltp.add("turn drive", cyl(360, c["face_off"] - 80, x=px, y=py, z=zt + 80), "r8s_abb_dk")
    spin = _piece(inst, "spin")
    spin.add("faceplate", cyl(c["face_d"], 40, x=px, y=py, z=zt + c["face_off"]), "steel")
    for k in range(6):
        zz = zt + c["face_off"] + 39
        spin.add(f"t-slot {k}", box(px + 120, py - 8, zz, px + 300, py + 8, zz + 2)
                 .rotate((px, py, 0), (px, py, 1), 30 + 60 * k), "inst_dark")
    spin.add("chuck", cyl(300, 40, x=px, y=py, z=zt + c["face_off"] + 40), "r8s_abb_dk")
    # the propeller (meshes), its patch, the beads; all ride the faceplate
    M0 = prop_mount(0.0)
    pm = propeller_meshes(damaged=True)
    inst.meshes["prop"] = [(pm["blades"].transform(M0, inplace=False), NAB_C, 1.0),
                           (pm["bore"].transform(M0, inplace=False), (0.25, 0.22, 0.20), 1.0)]
    inst.meshes["patch"] = [(pm["patch"].transform(M0, inplace=False), NAB_C, 1.0)]
    tl, beads, tilt = repair_program()
    T_ = tl.t[-1]
    v_of = {name: tl.t[i] / T_ for name, i in tl.marks.items()}
    beadj = {}
    for j, (segs, r) in enumerate(beads):
        for i, seg in enumerate(segs):
            mesh = _tube(seg, r, sides=10).transform(M0, inplace=False)
            name = f"bead{j}_{i}"
            inst.meshes[name] = [(mesh, BEAD_C, 1.0)]
            on = next(tl.t[n] / T_ for n, st in enumerate(tl.states) if (j, i) in st["built"])
            beadj[name] = Reveal(kind="reveal", parent="spin", on=on - 0.55 / T_ * 0.5, off=v_of["machined"],
                                 centre=tuple(mesh.center))
    # the robot: turret, lower arm, upper arm, wrist, the head
    bx, by, zs, Lt = _cell_k()
    S = (bx + c["a1"], by, zs)
    E = (S[0], by, zs + c["L2"])
    Wc = (S[0] + c["L3"], by, E[2])
    turret = _piece(inst, "j1")
    turret.add("turret", cyl(420, zs - c["riser"] - 150 - 60, x=bx, y=by, z=c["riser"] + 150), "r8s_abb")
    turret.add("shoulder housing", _ycyl(250, 300, x=S[0], y=by - 150, z=zs), "r8s_abb")
    lower = _piece(inst, "j2")
    lower.add("lower arm", box(S[0] - 70, by - 90, zs, S[0] + 70, by + 50, E[2]), "r8s_abb")
    lower.add("elbow housing", _ycyl(220, 200, x=E[0], y=by - 100, z=E[2]), "r8s_abb")
    upper = _piece(inst, "j3")
    upper.add("upper arm", box(E[0] - 60, by - 70, E[2] - 70, Wc[0] - 60, by + 70, E[2] + 70), "r8s_abb")
    upper.add("motor pack", box(E[0] - 260, by - 90, E[2] - 90, E[0] - 60, by + 90, E[2] + 90), "r8s_abb")
    upper.add("forearm", _xcyl(120, 70, x=Wc[0] - 70, y=by, z=Wc[2]), "r8s_abb_dk")
    wrist = _piece(inst, "j5")
    wrist.add("wrist", _ycyl(130, 150, x=Wc[0], y=by - 75, z=Wc[2]), "r8s_abb")
    wrist.add("flange", cyl(100, c["wrist"] - 60, x=Wc[0], y=by, z=Wc[2] - c["wrist"]), "r8s_abb_dk")
    hz1 = Wc[2] - c["wrist"]
    hz0 = hz1 - c["head_l"]
    wrist.add("printhead", box(Wc[0] - 131, by - 136, hz0 + 90, Wc[0] + 131, by + 136, hz1), "r8s_meltio")
    wrist.add("head front", box(Wc[0] - 100, by - 140, hz0 + 200, Wc[0] + 100, by - 136, hz1 - 60), "r8s_blue")
    wrist.add("nozzle", cq.Workplane("XY").circle(7).workplane(offset=90).circle(40).loft()
              .translate((Wc[0], by, hz0)), "copper")
    wrist.add("wire conduit", I._xcyl(30, 380, x=Wc[0] - 400, y=by + 100, z=hz1 - 60), "inst_black")
    glow = _piece(inst, "glow")
    tip = (Wc[0], by, hz0 - c["stand"])
    glow.add("blue cone", cq.Workplane("XY").circle(2).workplane(offset=c["stand"] + 2).circle(9).loft()
             .translate(tip), "r8s_blue")
    glow.add("melt pool", cq.Workplane().add(cq.Solid.makeSphere(5.5, cq.Vector(*tip), angleDegrees1=-90,
                                                                  angleDegrees2=90)), "r8s_glow")
    # the doors: slide apart
    doors = {}
    for k, sx in enumerate((-1, 1)):
        name = f"door{k}"
        dp = _piece(inst, name)
        x0, x1 = (ox0, 0.0) if sx < 0 else (0.0, ox1)
        dp.add("door frame", box(x0, yf - 60, 0, x1, yf - 20, c["door_h"]).cut(
            box(x0 + 70, yf - 61, c["low"], x1 - 70, yf - 19, c["door_h"] - 70)), "r8s_meltio")
        dp.add("door window", box(x0 + 70, yf - 50, c["low"], x1 - 70, yf - 30, c["door_h"] - 70), "r8s_amber")
        dp.add("door handle", box(-30 if sx < 0 else 10, yf - 110, 1000, -10 if sx < 0 else 30, yf - 60, 1400),
               "aluminium")
        doors[name] = Joint("slide", vec=(sx * (dw - 60), 0, 0))
    # joints
    knots = lambda f: tuple((t / T_, float(f(s))) for t, s in zip(tl.t, tl.states))       # noqa: E731
    pz = (0.0, by, zt)
    inst.joints = {
        **doors,
        "tilt": Turn(kind="turn", axis=(1, 0, 0), pivot=pz, knots=knots(lambda s: s["tilt"])),
        "spin": Joint("hinge", axis=(0, 0, 1), pivot=(px, py, 0), deg=120.0, parent="tilt"),
        "prop": Joint("slide", vec=(0, 0, 0), parent="spin"),
        "patch": Reveal(kind="reveal", parent="spin", on=v_of["machined"], off=9.0, centre=tuple(
            inst.meshes["patch"][0][0].center)),
        "j1": Turn(kind="turn", axis=(0, 0, 1), pivot=(bx, by, 0), knots=knots(lambda s: s["q"][0])),
        "j2": Turn(kind="turn", axis=(0, 1, 0), pivot=S, parent="j1", knots=knots(lambda s: s["q"][1])),
        "j3": Turn(kind="turn", axis=(0, 1, 0), pivot=E, parent="j2", knots=knots(lambda s: s["q"][2])),
        "j5": Turn(kind="turn", axis=(0, 1, 0), pivot=Wc, parent="j3", knots=knots(lambda s: s["q"][3])),
        **beadj,
    }
    # the melt pool and the blue cone: on from the first bead to the last (the gaps between passes are short)
    pools = [(tl.t[i] / T_, s["pool"]) for i, s in enumerate(tl.states)]
    on0 = min(v for v, p_ in pools if p_ > 0)
    inst.joints["glow"] = Reveal(kind="reveal", parent="j5", on=on0 - 0.3 / T_, off=v_of["deposited"],
                                 centre=tip)
    inst.program = dict(marks=v_of, tilt=tilt, T=T_, n_beads=len(beads))
    prog = ["tilt", "spin", "j1", "j2", "j3", "j5", "glow", "patch", *beadj]

    def go(a, b):
        return {k: (a, b) for k in prog if k != "spin"}
    inst.actions = [
        ("The Meltio Robot Cell: 4.05 x 2.35 x 3.0 m, an ABB robot and a two-axis positioner rated for 500 kg. Its "
         "two front doors slide apart.", 2.4, {"door0": (0.0, 1.0), "door1": (0.0, 1.0)}),
        ("On the positioner, a nickel aluminium bronze propeller after the WAAMpeller (1350 mm, about 400 kg), one "
         "blade's leading edge eroded.", 2.0, go(0.0, 0.0)),
        ("Doors shut. The positioner tilts the blade until the damaged edge faces up. Drawn see-through.", 2.4,
         {**go(0.0, v_of["tilted"]), "door0": (1.0, 0.0), "door1": (1.0, 0.0), "~body": (0.0, 0.8),
          "~door0": (0.0, 0.8), "~door1": (0.0, 0.8)}),
        ("The robot brings the head down over the edge.", 2.0, go(v_of["tilted"], v_of["approach"])),
        ("1 kW of blue light (nine 450 nm diodes) melts the wire into the cut-back edge, pass by pass, each layer "
         "standing on the last (beads drawn 2x).", 8.0, go(v_of["approach"], v_of["deposited"])),
        ("The head lifts and the robot goes home.", 2.0, go(v_of["deposited"], v_of["home"])),
        ("The overbuild is machined back to the blade's profile: the edge restored.", 2.0,
         go(v_of["home"], v_of["machined"])),
        ("The positioner levels the propeller.", 2.0, {**go(v_of["machined"], 1.0), "~body": (0.8, 0.0),
                                                       "~door0": (0.8, 0.0), "~door1": (0.8, 0.0)}),
    ]
    inst.labels = [("ABB robot with the\nblue-laser printhead", (Wc[0], by - 140, hz1 - 100), (0.14, 0.26)),
                   ("two-axis positioner, 500 kg", (px + 600, py - 200, zt + 100), (0.84, 0.62)),
                   ("NAB propeller, 1350 mm", (px - 300, py - 300, zt + 300), (0.84, 0.30))]
    inst.notes = ["4050 x 2350 x 3000 mm (Meltio); 4000 kg in the 2025 data sheet as indexed.",
                  "Takes 1000 mm dia. x 1200 mm printing with the positioner turning, 2000 x 1000 x 1000 mm with the "
                  "robot alone, 500 kg on the positioner: a 1350 mm, 400 kg propeller is repaired blade by blade."]
    inst.cam = (0.45, -2.0, 0.8)
    inst.framing = (0.95, 0.40)
    return inst


REGISTRY = {"eos_m400": eos_m400, "meltio_cell": meltio_cell}


if __name__ == "__main__":
    import json
    print(json.dumps(check_floor(), indent=1))
    tl, beads, tilt = repair_program()
    print("tilt", tilt, "beads", len(beads), "program", round(tl.t[-1], 1), "s")
    worst = 0.0
    for st in tl.states:
        fk = robot_fk(st["q"])
        worst = max(worst, float(np.linalg.norm(fk["W"] - fk["S"])))
    print("largest shoulder-wrist distance", round(worst), "of", CELL["L2"] + CELL["L3"])

"""The tray's media coupling, part by part (#303, PR #318).

Sterling, PR #318, 2026-11-18: "I think we need something more real and high-fidelity for the liquid, gas, and power
transfer modules (quick disconnect, etc.) for the VLM". Round 4's coupling (services.py) was a 200 x 90 mm block with
six flat discs and bars standing for the inserts, two pins and a box for the dock. This module draws the parts
themselves, from Staubli's CombiTac uniq main catalogue (CT-Main-11014009-en, 08.2026) and its CombiTac align flyer
(11014023-en), and puts them into a dock that fits the space the Shuttle leaves beside a tray.

    xvfb-run -a python3 coupling.py movie        # the close-up: out/vlm_coupling.gif, out/mp4/vlm_coupling.mp4
    xvfb-run -a python3 coupling.py stills       # out/coupling/*.png: the halves, the dock, sections
    python3 coupling.py json                     # out/coupling.json: the parts list, forces, stroke, clearances

What is Staubli's and what is ours:
* Staubli's (catalogue numbers in SOURCES): the CombiTac carriers and their widths, the contacts and their order of
  mating (PE first, LMFB last), the 10 Gbit module, the SCT03 and LCT06 couplings with their hex sizes and lengths,
  the align 4 end pieces (CT-HME-S/4 and -B/4: a 9.8 mm pin 50.2 mm proud of an 18 mm body, 34.7 x 43 mm), the
  supporting rails, the panel cut-outs (L + 54 x 41 mm, holes at L + 70) and the 25 mm between mated panels.
* Ours: the panels, the bracket on the tray, the floating plate, the carriage on two MGN12 guides, the slider-crank
  drive and its worm gearmotor, the energy chain and the valve bank. Their sizes are chosen to fit, not sourced.
* Drawn, not dimensioned by Staubli: pin lengths (the catalogue gives their order, not their lengths), the insides of
  the couplings (the principle is the flat-face, double shut-off one; the parts inside are not published), the
  carriers' height between the rails (30 mm, from the 10 Gbit module's 28-32 mm drawing).

Frames: the slot's (services.py), x across the tray towards the right-hand side wall, y along the tray's depth, z up
from the tray's underside, mm. The mating plane is X_M; the dock's head sits at s = 0 when mated and STROKE when
pulled back (s along +x).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import cadquery as cq
import numpy as np

import vlm as V

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lab_models"))
from common import box  # noqa: E402

OUT = HERE / "out"

# ===================================================================================================== sources
SOURCES = {
    "widths": "CombiTac uniq main catalogue (CT-Main-11014009-en) p.83 'Calculation of installation dimensions': "
              "carrier widths CT-E3-3 and CT-E3-2+PE 10 mm, CT-LMFB 6 mm, CT-10GBIT 22 mm, CT-E8-2 18 mm, "
              "CT-E-UCT08-2 42 mm, spacer CT-DIP4 4 mm; recess L1 = L + 22 / L2 = L + 33 for standard end pieces.",
    "carrier_depth": "p.22, p.74: carriers 24 mm deep (mating axis); p.48: CT-10GBIT 34.9 mm deep, 28-32 mm tall, "
                     "its pins 12 mm proud on the pin side, an RJ45 jack at the back.",
    "align4": "p.80-81 and CombiTac align flyer (11014023-en) p.12-13: CT-HME-S/4 (pin part) and CT-HME-B/4 (socket "
              "part), zinc die-cast, 18 mm thick, 34.7 mm tall, 43 mm long, pin O9.8 mm 50.2 mm proud of the body "
              "(68.2 overall) with an insulating cap, pin axis 13.5 mm and screw hole 35 mm from the carriers' end; "
              "radial misalignment 4 mm, angular +-2 deg, 100,000 mating cycles. 'In a permanent installation "
              "application, the customer must provide a stable guide system'.",
    "cutout": "p.84: panel cut-out for high-misalignment end pieces L + 54 x 41 mm, R5 corners, 2 x O4.2 mm holes at "
              "L + 70 mm.",
    "mated_gap": "p.86: distance between the panels when mated Z = 25 mm (+1.5); p.87: largest gap between mated "
                 "carriers 1-2 mm by contact (LCT06, LMFB 1 mm; CT3, SCT03, RJ45 2 mm; 10 Gbit 1.5 mm).",
    "ct3": "p.26-29: O3 mm power unit up to 39 A, 3-pole CT-E3-3 and CT-E3-2+PE (one pole a protective earth); "
           "average sliding force 8 N per contact; 'Longer type of pin mates first'.",
    "lmfb": "p.40-41: Last Mate First Break module CT-LMFB/B and /S, two contacts at the carrier's edge positions, "
            "'intended for monitoring purposes, and show whether a CombiTac is fully connected or not'; 100 mA, "
            "14 N spring force per contact.",
    "gbit": "p.48-49: CT-10GBIT-RJ45/B and /S, Ethernet to 10 Gbit/s (Cat6A), 14 N average sliding force per module, "
            "100,000 mating cycles.",
    "sct03": "p.72-73: CT-B-SCT03 and CT-S-SCT03 in carrier CT-E8-2, G1/8 internal thread, SW12, 15 + 25 mm (socket) "
             "and 10.5 + 25 + 15 mm (plug), nominal bore 3 mm, 15 bar, 'leakproof, shut-off on both sides', spring "
             "force 43 N without pressure. p.61, p.70: fluid couplings 'can also be used for pneumatic "
             "applications, if a shut-off valve on both sides is needed'.",
    "lct06": "p.74-75: CT-B-LCT06 and CT-S-LCT06 in carrier CT-E-UCT08-2, G1/4 internal thread, SW17, 20.5 + 24 mm "
             "(socket) and 11 + 24 + 8.5 mm (plug), nominal bore 6 mm, 15 bar, 8.48 L/min at 5 m/s, spring force "
             "44.5 N without pressure, 135 N while mated at 10 bar; 'Connecting and disconnecting under pressure is "
             "prohibited.'",
    "safety": "p.137: 'On permanently fixed installations, electrical contacts have to be placed above liquid "
              "couplings'; 'Connecting and disconnecting when live is permitted. Connecting and disconnecting under "
              "load is not permitted.' p.139: the socket side is touch-protected (IP2X) when disconnected.",
    "mating_speed": "p.135: 'CombiTac was tested at a mating speed of 600 mm/min by an automatic process. Plugging "
                    "force is equal to 1.5 times the sliding force.'",
    "hard_stop": "p.82: screw CT-SHR-HS (M4) gives the end pieces a hard stop 'so that the force does not impact on "
                 "the contacts during the mating process'.",
    "mgn12": "HIWIN MGN12H miniature guide: rail 12 x 8 mm, block 27 mm wide, 45.4 mm long (hiwin.com MG series).",
    "igus": "igus E2 micro energy chains, e.g. series E2.15 (inner height 15 mm, bend radii from 18 mm): our size, "
            "not a selected part.",
}

# ===================================================================================================== layout
X_M = V.TRAY_W / 2 - 6.0          # 1219: the mating plane, 6 mm inside the tray's side, as round 7 had it
YC = V.TRAY_D / 2 - 12 - 140      # 280: the coupling's centre along the tray (services.PLATE_Y)
Z_F, Z_E = 40.0, 88.0             # the fluid frame and, above it (p.137), the electrical frame: centre heights
END = dict(w=43.0, t=18.0, h=34.7, pin_d=9.8, pin_l=50.2, pin_at=13.5, hole_at=35.0, flange_t=12.5)
CARRIER = dict(depth=24.0, h=30.0, rail_h=2.35, rail_d=10.0)
PANEL = dict(t=6.0, y0=YC - 90.0, y1=YC + 90.0, z0=12.0, z1=118.0, half_gap=12.5)   # 25 mm between mated panels
STROKE = 75.0                     # pulled back: the align pins' tips 18.8 mm clear of the tray's side (clear_mm())
SIDE = V.TRAY_W / 2               # 1225, the tray's side
WALL_X = V.TRAY_W / 2 + 45        # 1270, the column side wall's inner face (12 mm sheet)
CLAD_X = V.UNIT_W / 2             # 1390, the cladding's inner face

# Each frame's modules, left to right along +y: (key, width, [(dy, dz, what, medium)]) with dy, dz from the module's
# centre. Electrical: LMFB, PE (with two spare poles), L1/L2/N, a spacer, 10 Gbit. Fluid: air and N2 on SCT03,
# chilled water in and out on LCT06 (p.137: liquids below the electrics).
E_MODS = [
    ("CT-LMFB", 6.0, [(0.0, 11.0, "lmfb", "lmfb"), (0.0, -11.0, "lmfb", "lmfb")]),
    ("CT-E3-2+PE", 10.0, [(0.0, 9.0, "spare", None), (0.0, 0.0, "pe", "power"), (0.0, -9.0, "spare", None)]),
    ("CT-E3-3", 10.0, [(0.0, 9.0, "ct3", "power"), (0.0, 0.0, "ct3", "power"), (0.0, -9.0, "ct3", "power")]),
    ("CT-DIP4", 4.0, []),
    ("CT-10GBIT-RJ45", 22.0, [(-5.5, 7.5, "gbit", "data"), (5.5, 7.5, "gbit", "data"), (-5.5, -7.5, "gbit", "data"),
                              (5.5, -7.5, "gbit", "data")]),
]
F_MODS = [
    ("CT-E8-2 + 2 x SCT03", 18.0, [(0.0, 8.0, "sct", "air"), (0.0, -8.0, "sct", "n2")]),
    ("CT-E-UCT08-2 + 2 x LCT06", 42.0, [(-10.5, 0.0, "lct", "cws"), (10.5, 0.0, "lct", "cwr")]),
]
FRAMES = {"E": (Z_E, E_MODS), "F": (Z_F, F_MODS)}
WIRE_C = {"L1": (0.42, 0.26, 0.15), "L2": (0.12, 0.12, 0.13), "N": (0.20, 0.35, 0.75), "PE": (0.35, 0.62, 0.25)}

# how far each contact's pin (or the coupling's nose) stands proud of the pin-side carrier's face: Staubli gives the
# order (PE first, LMFB last) and the 10 Gbit pins' 12 mm; the rest are drawn so that the order holds
PROUD = {"pe": 12.5, "ct3": 10.0, "lmfb": 7.0, "gbit": 12.0, "sct": 10.5, "lct": 11.0}
# the couplings (p.73, p.75): socket front, socket body; plug nose, plug body, plug rear; across flats; nose and
# sleeve diameters; the tube's outer diameter; the thread
CPL = {"sct": dict(s_front=15.0, s_body=25.0, p_nose=10.5, p_body=25.0, p_rear=15.0, sw=12.0, nose_d=8.0,
                   sleeve_d=11.5, bore=3.0, tube=6.0, thread="G1/8", spring=43.0),
       "lct": dict(s_front=20.5, s_body=24.0, p_nose=11.0, p_body=24.0, p_rear=8.5, sw=17.0, nose_d=12.0,
                   sleeve_d=16.0, bore=6.0, tube=8.0, thread="G1/4", spring=44.5)}
SLIDING = {"ct3": 8.0, "pe": 8.0, "lmfb": 14.0, "gbit": 14.0}    # N per contact (per module for 10 Gbit), p.21-49

# the dock (ours). Carriage on two MGN12 rails under the top plate; slider-crank drive beside the head (+y), its
# crank turned 180 deg between two dead centres, so the coupling's springs can't push it back at either end.
DOCK = dict(y0=YC - 110.0, y1=YC + 178.0, x0=WALL_X - 20.0, x1=CLAD_X - 2.0, z0=0.0, z1=158.0, t=6.0)
RAIL_Y = (YC - 60.0, YC + 60.0)
CARRIAGE_X = 1299.0               # the carriage plate's front face when mated
CRANK = dict(r=STROKE / 2, L=50.0, y=YC + 136.0, z=68.0)
CRANK["x"] = CARRIAGE_X + 3.0 - CRANK["L"] + CRANK["r"]      # the crank's axis: the drive pin at its nearest when mated
CHAIN = dict(x_fixed=1292.0, x_end0=1292.0, straight=73.0, r=22.0, z_up=-14.0, w=64.0, h=20.0, pitch=13.0,
             y=YC - 14.0)
VALVES_Z = (-178.0, -96.0)


def drive_s(phi: float) -> float:
    """The head's travel s (0 mated .. STROKE pulled back) at crank angle phi (0 .. pi): slider-crank, both ends dead
    centres."""
    r, L = CRANK["r"], CRANK["L"]
    x = -r * math.cos(phi) + math.sqrt(L * L - (r * math.sin(phi)) ** 2)     # pin from the crank's axis, along +x
    return x - (L - r)


def drive_phi(s: float) -> float:
    """The crank angle for travel s (inverse of drive_s, by bisection)."""
    lo, hi = 0.0, math.pi
    s = min(max(s, 0.0), STROKE)
    for _ in range(50):
        mid = (lo + hi) / 2
        if drive_s(mid) < s:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ===================================================================================================== materials
MATERIALS = {
    "cpl_carrier": (0.11, 0.11, 0.12, 1.0, 0.25),      # black EPTR / PA carriers
    "cpl_zinc": (0.72, 0.73, 0.74, 1.0, 0.55),         # die-cast zinc end pieces
    "cpl_bronze": (0.74, 0.55, 0.30, 1.0, 0.6),        # the cone's bushing
    "cpl_insul": (0.08, 0.08, 0.09, 1.0, 0.35),        # the guide pin's insulating cap
    "cpl_pin": (0.80, 0.81, 0.82, 1.0, 0.8),           # hardened guide pins
    "cpl_silver": (0.86, 0.86, 0.84, 1.0, 0.85),       # silver-plated contacts (MULTILAM)
    "cpl_nickel": (0.79, 0.79, 0.77, 1.0, 0.75),       # nickel-plated brass couplings
    "cpl_stainless": (0.70, 0.71, 0.72, 1.0, 0.7),
    "cpl_alu": (0.66, 0.68, 0.70, 1.0, 0.45),          # clear-anodised plates
    "cpl_alu_dark": (0.30, 0.31, 0.33, 1.0, 0.4),      # the dock's frame, dark anodised
    "cpl_steel": (0.55, 0.56, 0.58, 1.0, 0.6),         # rails, blocks, screws
    "cpl_spring": (0.40, 0.41, 0.43, 1.0, 0.6),
    "cpl_motor": (0.17, 0.18, 0.19, 1.0, 0.35),
    "cpl_gearbox": (0.52, 0.53, 0.55, 1.0, 0.4),
    "cpl_chain": (0.16, 0.16, 0.17, 1.0, 0.25),        # igus black
    "cpl_fitting": (0.85, 0.85, 0.83, 1.0, 0.6),       # push-in fittings, nickel-plated
    "cpl_collet": (0.20, 0.42, 0.75, 1.0, 0.3),        # the fittings' blue release collets
    "cpl_valve": (0.20, 0.21, 0.23, 1.0, 0.35),
    "cpl_coil": (0.10, 0.10, 0.11, 1.0, 0.3),
    "cpl_din": (0.88, 0.88, 0.86, 1.0, 0.25),          # the contactor's and relay's grey housings
    "cpl_hole": (0.03, 0.03, 0.04, 1.0, 0.1),          # socket mouths
    "cpl_seal": (0.15, 0.15, 0.16, 1.0, 0.2),          # NBR seals
    "cpl_cat6": (0.20, 0.55, 0.30, 1.0, 0.3),          # Cat 6A cable
    "cpl_cable": (0.12, 0.12, 0.13, 1.0, 0.3),         # mains cable jacket
    "cpl_wire_l1": (*WIRE_C["L1"], 1.0, 0.3), "cpl_wire_l2": (*WIRE_C["L2"], 1.0, 0.3),
    "cpl_wire_n": (*WIRE_C["N"], 1.0, 0.3), "cpl_wire_pe": (*WIRE_C["PE"], 1.0, 0.3),
    "cpl_wire_sig": (0.85, 0.85, 0.30, 1.0, 0.3),      # the LMFB loop's thin yellow wires
    "cpl_tube_air": (0.25, 0.48, 0.80, 1.0, 0.3),      # blue PU for air
    "cpl_tube_n2": (0.12, 0.12, 0.13, 1.0, 0.3),       # black for N2
    "cpl_tube_cws": (0.25, 0.45, 0.85, 0.9, 0.35),     # water in, blue
    "cpl_tube_cwr": (0.80, 0.22, 0.20, 0.9, 0.35),     # water out, red
    "cpl_sensor": (0.80, 0.55, 0.12, 1.0, 0.4),        # inductive proximity sensors (brass)
    "cpl_wall": (0.78, 0.80, 0.83, 0.30, 0.1),
    "cpl_tray": (0.42, 0.45, 0.50, 1.0, 0.3),
    "cpl_rib": (0.66, 0.68, 0.71, 1.0, 0.3),
    "cpl_water": (0.35, 0.60, 0.85, 0.7, 0.6),
}
TUBE_MAT = {"air": "cpl_tube_air", "n2": "cpl_tube_n2", "cws": "cpl_tube_cws", "cwr": "cpl_tube_cwr"}


# ===================================================================================================== primitives
def xcyl(d, x0, x1, y, z) -> cq.Workplane:
    lo, hi = min(x0, x1), max(x0, x1)
    return cq.Workplane("YZ").circle(d / 2).extrude(hi - lo).translate((lo, y, z))


def xtube(od, idia, x0, x1, y, z) -> cq.Workplane:
    lo, hi = min(x0, x1), max(x0, x1)
    return cq.Workplane("YZ").circle(od / 2).circle(idia / 2).extrude(hi - lo).translate((lo, y, z))


def xhex(sw, x0, x1, y, z) -> cq.Workplane:
    lo, hi = min(x0, x1), max(x0, x1)
    return cq.Workplane("YZ").polygon(6, sw / math.cos(math.radians(30))).extrude(hi - lo).translate((lo, y, z))


def xcone(d0, d1, x0, x1, y, z) -> cq.Workplane:
    """Frustum along x: diameter d0 at x0, d1 at x1."""
    s = cq.Solid.makeCone(d0 / 2, d1 / 2, abs(x1 - x0), cq.Vector(x0, y, z), cq.Vector(1 if x1 > x0 else -1, 0, 0))
    return cq.Workplane().add(s)


def zcyl(d, z0, z1, x, y) -> cq.Workplane:
    return cq.Workplane("XY").circle(d / 2).extrude(z1 - z0).translate((x, y, z0))


def ycyl(d, y0, y1, x, z) -> cq.Workplane:
    lo, hi = min(y0, y1), max(y0, y1)
    return cq.Workplane("XZ").circle(d / 2).extrude(-(hi - lo)).translate((x, lo, z))


def rrect_x(x0, x1, y0, y1, z0, z1, r) -> cq.Workplane:
    """A box along x with rounded edges round x (a panel cut-out, say)."""
    w, h = y1 - y0, z1 - z0
    sk = cq.Workplane("YZ").sketch().rect(w, h).vertices().fillet(r).finalize()
    return sk.extrude(x1 - x0).translate((x0, (y0 + y1) / 2, (z0 + z1) / 2))


def helix_x(d, wire, x0, x1, y, z, turns) -> cq.Workplane:
    """A coil spring along x: wire diameter `wire`, coil diameter d."""
    L = x1 - x0
    hx = cq.Wire.makeHelix(pitch=L / turns, height=L, radius=d / 2)
    prof = cq.Workplane("XZ").center(d / 2, 0).circle(wire / 2)
    spring = prof.sweep(cq.Workplane().add(hx), isFrenet=True)
    return spring.rotate((0, 0, 0), (0, 1, 0), 90).translate((x0, y, z))


def poly_tube(pts, d) -> cq.Workplane:
    """A tube or cable through waypoints, with rounded bends (fillets where it turns)."""
    from common import hose
    clean = [pts[0]]
    for q in pts[1:]:
        if math.dist(q, clean[-1]) > 0.5:
            clean.append(q)
    return hose(clean, d)


# ===================================================================================================== a frame
def frame_span(mods) -> tuple:
    """(L, [(key, y0, y1, poles)]) of a frame's modules, centred on YC."""
    L = sum(w for _, w, _ in mods)
    y = YC - L / 2
    out = []
    for key, w, poles in mods:
        out.append((key, y, y + w, poles))
        y += w
    return L, out


def pole_points(which: str) -> list:
    """[(world y, z, what, medium, module key)] of every pole of frame E or F."""
    zc, mods = FRAMES[which]
    _, span = frame_span(mods)
    out = []
    for key, y0, y1, poles in span:
        ym = (y0 + y1) / 2
        for dy, dz, what, medium in poles:
            out.append((ym + dy, zc + dz, what, medium, key))
    return out


def end_axes(which: str) -> list:
    """[(y of the align pin's axis, y of the screw hole, z)] at both ends of frame E or F."""
    zc, mods = FRAMES[which]
    L, _ = frame_span(mods)
    out = []
    for sgn in (-1, 1):
        out.append((YC + sgn * (L / 2 + END["pin_at"]), YC + sgn * (L / 2 + END["hole_at"]), zc))
    return out


def _carrier(which, side) -> dict:
    """The carriers, rails and contacts of frame E or F on one side ('socket' on the tray, 'pin' on the dock)."""
    zc, mods = FRAMES[which]
    L, span = frame_span(mods)
    sg = -1.0 if side == "socket" else 1.0          # the carriers lie on -x of the mating plane (tray) or +x (dock)
    D = CARRIER["depth"]
    p = {}
    bodies, holes = [], []
    for key, y0, y1, poles in span:
        if key == "CT-DIP4":
            p[f"{which} spacer"] = (box(min(X_M, X_M + sg * D), y0, zc - CARRIER["h"] / 2, max(X_M, X_M + sg * D), y1,
                                        zc + CARRIER["h"] / 2), "cpl_carrier")
            continue
        depth = 34.9 if key.startswith("CT-10GBIT") else D
        b = box(min(X_M, X_M + sg * depth), y0 + 0.15, zc - CARRIER["h"] / 2, max(X_M, X_M + sg * depth), y1 - 0.15,
                zc + CARRIER["h"] / 2)
        if key.startswith("CT-10GBIT"):              # the RJ45 jack's housing, narrower than the carrier, at the back
            b = box(min(X_M, X_M + sg * D), y0 + 0.15, zc - CARRIER["h"] / 2, max(X_M, X_M + sg * D), y1 - 0.15,
                    zc + CARRIER["h"] / 2).union(
                box(min(X_M + sg * D, X_M + sg * depth), y0 + 1.5, zc - 14, max(X_M + sg * D, X_M + sg * depth),
                    y1 - 1.5, zc + 14))
        ym = (y0 + y1) / 2
        for dy, dz, what, medium in poles:
            y, z = ym + dy, zc + dz
            if what in ("sct", "lct"):
                c = CPL[what]
                holes.append(xcyl(c["sleeve_d"] + 0.6 if side == "socket" else c["sw"] / math.cos(math.radians(30)) + 0.4,
                                  X_M - 0.1 * sg, X_M + sg * (D + 0.2), y, z))
            elif side == "socket" and what != "spare":
                dd = {"lmfb": 3.0, "gbit": 5.0}.get(what, 4.6)
                holes.append(xcyl(dd, X_M + 0.1, X_M - 14.0, y, z))
        bodies.append((key, b))
    for key, b in bodies:
        for h in holes:
            b = b.cut(h)
        p[f"{which} carrier {key}"] = (b, "cpl_carrier")
    # the supporting rails, top and bottom, into the end pieces
    for s in (-1, 1):
        zr0 = zc + s * CARRIER["h"] / 2
        zr1 = zr0 + s * CARRIER["rail_h"]
        xa, xb = X_M + sg * 7.0, X_M + sg * (7.0 + CARRIER["rail_d"])
        p[f"{which} rail {'top' if s > 0 else 'bottom'}"] = (
            box(min(xa, xb), YC - L / 2 - 27, min(zr0, zr1), max(xa, xb), YC + L / 2 + 27, max(zr0, zr1)), "cpl_alu")
    # contacts
    socks, pins, pe, lm, gb, plugs_or_socks = [], [], [], [], [], []
    for key, y0, y1, poles in span:
        ym = (y0 + y1) / 2
        for dy, dz, what, medium in poles:
            y, z = ym + dy, zc + dz
            if what == "spare":
                if side == "socket":         # a blind plug in the socket
                    socks.append(xcyl(4.4, X_M - 0.6, X_M - 3.0, y, z))
                continue
            if what in ("sct", "lct"):
                continue
            if side == "socket":
                od = {"lmfb": 2.8, "gbit": 4.8}.get(what, 4.4)
                idd = {"lmfb": 1.6, "gbit": 2.6}.get(what, 3.1)
                socks.append(xtube(od, idd, X_M - 2.0, X_M - 14.0, y, z))
            else:
                d = {"lmfb": 1.5, "gbit": 2.5}.get(what, 3.0)
                L0 = PROUD[what]
                pin = xcyl(d, X_M - L0 + 1.0, X_M + 3.0, y, z).union(xcone(d, d * 0.55, X_M - L0 + 1.0, X_M - L0, y, z))
                if what == "gbit":           # the coax-like contacts' insulating sleeve
                    pin = pin.union(xtube(4.6, 2.6, X_M - 3.0, X_M + 0.5, y, z))
                (pe if what == "pe" else lm if what == "lmfb" else gb if what == "gbit" else pins).append(pin)
    for name, lst in (("sockets", socks), ("pins", pins), ("PE pin", pe), ("LMFB pins", lm), ("10 Gbit pins", gb)):
        if lst:
            s = lst[0]
            for o in lst[1:]:
                s = s.union(o)
            p[f"{which} {name}"] = (s, "cpl_silver")
    return p


def _end_pieces(which, side) -> dict:
    """The two align 4 end pieces of frame E or F: CT-HME-B/4 (cone) on the tray, CT-HME-S/4 (pin) on the dock."""
    zc, mods = FRAMES[which]
    L, _ = frame_span(mods)
    sg = -1.0 if side == "socket" else 1.0
    E = END
    p = {}
    for i, sgn in enumerate((-1, 1)):
        ya = YC + sgn * L / 2                        # the carriers' end
        yb = ya + sgn * 27.0                         # through the cut-out
        yc_ = ya + sgn * E["w"]                      # the flange's end
        inner = box(min(X_M, X_M + sg * E["t"]), min(ya, yb), zc - E["h"] / 2, max(X_M, X_M + sg * E["t"]),
                    max(ya, yb), zc + E["h"] / 2)
        flange = box(min(X_M, X_M + sg * E["flange_t"]), min(yb, yc_), zc - E["h"] / 2 + 2,
                     max(X_M, X_M + sg * E["flange_t"]), max(yb, yc_), zc + E["h"] / 2 - 2)
        body = inner.union(flange)
        try:
            body = body.edges("|X").fillet(2.0)
        except Exception:                            # noqa: BLE001
            pass
        ypin, yhole, _ = end_axes(which)[i]
        # the screw's counterbore (a filister-head M4 from the mating side, as the catalogue's pictures show)
        body = body.cut(xcyl(7.5, X_M - sg * 0.1, X_M + sg * 4.5, yhole, zc)).cut(
            xcyl(4.2, X_M, X_M + sg * E["flange_t"] + sg, yhole, zc))
        p[f"{which} end {i} screw"] = (xcyl(6.8, X_M + sg * 4.5, X_M + sg * 8.0, yhole, zc).union(
            xcyl(4.0, X_M + sg * 8.0, X_M + sg * (E["flange_t"] + PANEL["t"] + 3.0), yhole, zc)), "cpl_steel")
        if side == "socket":
            cone = xcone(24.0, 10.4, X_M + 0.1, X_M - 9.0, ypin, zc).union(xcyl(10.4, X_M - 9.0, X_M - E["t"] - 1, ypin, zc))
            body = body.cut(cone)
            p[f"{which} end {i} bushing"] = (xtube(14.0, 10.0, X_M - 9.0, X_M - E["t"], ypin, zc), "cpl_bronze")
        else:
            p[f"{which} end {i} pin"] = (xcyl(E["pin_d"], X_M - 42.2, X_M + 1.0, ypin, zc).union(
                xcyl(15.0, X_M - 1.5, X_M + 0.5, ypin, zc)), "cpl_pin")
            p[f"{which} end {i} pin cap"] = (xcone(E["pin_d"], 3.5, X_M - 42.2, X_M - E["pin_l"] + 0.6, ypin, zc).union(
                cq.Workplane().add(cq.Solid.makeSphere(1.75, cq.Vector(X_M - E["pin_l"] + 1.6, ypin, zc)))),
                "cpl_insul")
            # Staubli's hard-stop screw CT-SHR-HS (p.82): its head stands 0.5 mm proud, so the carriers stop 0.5 mm
            # apart and the contacts take no force
            p[f"{which} end {i} hard stop"] = (xcyl(5.5, X_M - 0.5, X_M + 0.5, yhole + sgn * -12.0, zc - 9.0),
                                               "cpl_steel")
        p[f"{which} end {i}"] = (body, "cpl_zinc")
    return p


def _couplings(side, internals=True) -> dict:
    """The fluid couplings' outsides (and, with internals, their valve parts in the disconnected position) on one side,
    plus their push-in fittings."""
    p = {}
    for y, z, what, medium, key in pole_points("F"):
        c = CPL[what]
        swd = c["sw"]
        if side == "socket":
            front = xtube(c["sleeve_d"], c["nose_d"] + 0.3, X_M - c["s_front"], X_M - 0.3, y, z)
            body = xhex(swd, X_M - c["s_front"] - c["s_body"], X_M - c["s_front"], y, z)
            p[f"socket {medium} body"] = (front.union(body), "cpl_nickel")
            if internals:      # the fixed central piston, flush with the face; the sliding sleeve round it
                p[f"socket {medium} piston"] = (xcyl(c["nose_d"] * 0.58, X_M - c["s_front"] - 4, X_M - 0.4, y, z),
                                                "cpl_stainless")
                p[f"socket {medium} sleeve"] = (xtube(c["nose_d"] + 0.2, c["nose_d"] * 0.6, X_M - c["s_front"] + 4,
                                                      X_M - 0.4, y, z), "cpl_stainless")
            fx0 = X_M - c["s_front"] - c["s_body"]
            fit = xcyl(c["tube"] + 5.0, fx0 - 16.0, fx0, y, z).union(xhex(c["tube"] + 6.0, fx0 - 5.0, fx0, y, z))
            p[f"socket {medium} fitting"] = (fit, "cpl_fitting")
            p[f"socket {medium} collet"] = (xtube(c["tube"] + 3.5, c["tube"], fx0 - 19.0, fx0 - 16.0, y, z), "cpl_collet")
        else:
            nose = xtube(c["nose_d"], c["nose_d"] * 0.6, X_M - c["p_nose"], X_M + 0.5, y, z)
            body = xhex(swd, X_M + 0.5, X_M + c["p_body"], y, z).union(
                xhex(swd, X_M + c["p_body"] + 1.0, X_M + c["p_body"] + c["p_rear"], y, z)).union(
                xcyl(swd * 0.8, X_M + c["p_body"], X_M + c["p_body"] + 1.0, y, z))
            p[f"plug {medium} body"] = (nose.union(body), "cpl_nickel")
            if internals:      # the plug's spring-loaded poppet, flush with the nose
                p[f"plug {medium} poppet"] = (xcyl(c["nose_d"] * 0.6 - 0.2, X_M - c["p_nose"] + 0.2, X_M + 6.0, y, z),
                                              "cpl_stainless")
            fx0 = X_M + c["p_body"] + c["p_rear"]
            fit = xcyl(c["tube"] + 5.0, fx0, fx0 + 16.0, y, z).union(xhex(c["tube"] + 6.0, fx0, fx0 + 5.0, y, z))
            p[f"plug {medium} fitting"] = (fit, "cpl_fitting")
            p[f"plug {medium} collet"] = (xtube(c["tube"] + 3.5, c["tube"], fx0 + 16.0, fx0 + 19.0, y, z), "cpl_collet")
    return p


def _panel(side) -> cq.Workplane:
    """The plate the two frames are mounted in (ours): 6 mm aluminium with Staubli's cut-outs and holes."""
    sg = -1.0 if side == "socket" else 1.0
    xa = X_M + sg * PANEL["half_gap"]
    xb = xa + sg * PANEL["t"]
    pl = box(min(xa, xb), PANEL["y0"], PANEL["z0"], max(xa, xb), PANEL["y1"], PANEL["z1"])
    try:
        pl = pl.edges("|X").fillet(6.0)
    except Exception:                                # noqa: BLE001
        pass
    for which, (zc, mods) in FRAMES.items():
        L, _ = frame_span(mods)
        pl = pl.cut(rrect_x(min(xa, xb) - 1, max(xa, xb) + 1, YC - (L + 54) / 2, YC + (L + 54) / 2, zc - 20.5, zc + 20.5,
                            5.0))
        for _, yh, _ in end_axes(which):
            pl = pl.cut(xcyl(4.2, xa - sg, xb + sg, yh, zc))
    return pl


# ===================================================================================================== the tray's half
def tray_half(internals=True) -> dict:
    """Everything on the tray (socket side), tray frame: {name: (shape, material)}."""
    p = {"tray panel": (_panel("socket"), "cpl_alu")}
    xa = X_M - PANEL["half_gap"] - PANEL["t"]          # the panel's back: 1200.5
    # the bracket: a base plate on the tray floor and two gussets, bolted to the panel's back (ours)
    base = box(xa - 70.0, PANEL["y0"], V.T_FLOOR, xa, PANEL["y1"], V.T_FLOOR + 5.0)
    gus = None
    for yg in (PANEL["y0"], PANEL["y1"] - 4.0):
        g = cq.Workplane("XZ").polyline([(xa - 70.0, V.T_FLOOR + 5), (xa, V.T_FLOOR + 5), (xa, PANEL["z1"] - 4),
                                         (xa - 12.0, PANEL["z1"] - 4)]).close().extrude(-4.0).translate((0, yg, 0))
        gus = g if gus is None else gus.union(g)
    p["tray bracket"] = (base.union(gus), "cpl_alu_dark")
    for which in FRAMES:
        p.update(_carrier(which, "socket"))
        p.update(_end_pieces(which, "socket"))
    p.update(_couplings("socket", internals))
    p.update(_terminations("socket"))
    return p


def _terminations(side) -> dict:
    """Crimp barrels and wires, the 10 Gbit module's RJ45 plug and cable, the LMFB loop: behind the carriers."""
    sg = -1.0 if side == "socket" else 1.0
    D = CARRIER["depth"]
    p = {}
    xb = X_M + sg * D                                 # the carriers' back
    wires = {}
    names = iter(["L1", "L2", "N"])
    lm = []
    for y, z, what, medium, key in pole_points("E"):
        if what in ("ct3", "pe"):
            nm = "PE" if what == "pe" else next(names)
            barrel = xcyl(5.2, xb, xb + sg * 11.0, y, z)
            p.setdefault("crimp barrels", []).append(barrel)
            # each wire leaves its barrel, turns towards the cable gland and joins the others
            wires[nm] = [(xb + sg * 11.0, y, z), (xb + sg * 22.0, y, z), (xb + sg * 30.0, YC - 8.0, Z_E + 26.0)]
        elif what == "lmfb":
            lm.append((y, z))
        elif what == "gbit":
            pass
    out = {}
    if "crimp barrels" in p:
        s = p["crimp barrels"][0]
        for o in p["crimp barrels"][1:]:
            s = s.union(o)
        out["crimp barrels"] = (s, "cpl_silver")
    for nm, pts in wires.items():
        out[f"wire {nm}"] = (poly_tube(pts, 3.2), f"cpl_wire_{nm.lower()}")
    # the mains cable: from the gland behind the carriers, out of the way of the align pins' tips (to x 1168.8)
    gx = xb + sg * 30.0
    if side == "socket":
        cable = [(gx, YC - 8.0, Z_E + 26.0), (gx - 30.0, YC - 8.0, Z_E + 40.0), (gx - 60.0, YC - 8.0, Z_E + 48.0)]
    else:
        cable = [(gx, YC - 8.0, Z_E + 26.0), (gx + 10.0, YC - 8.0, Z_E + 26.0)]
    out["mains gland"] = (xcyl(14.0, gx, gx + sg * 9.0, YC - 8.0, Z_E + 26.0) if side == "pin" else
                          xcyl(14.0, gx - 9.0, gx, YC - 8.0, Z_E + 26.0), "cpl_cable")
    out["mains cable"] = (poly_tube(cable, 10.5), "cpl_cable")
    # the 10 Gbit module's RJ45 plug and its Cat 6A cable
    _, span = frame_span(E_MODS)
    gy = [(a + b) / 2 for k, a, b, _ in span if k.startswith("CT-10GBIT")][0]
    gx0 = X_M + sg * 34.9
    out["RJ45 plug"] = (box(min(gx0, gx0 + sg * 20.0), gy - 6.0, Z_E - 7.0, max(gx0, gx0 + sg * 20.0), gy + 6.0, Z_E + 7.0),
                        "cpl_hole")
    cat = [(gx0 + sg * 20.0, gy, Z_E), (gx0 + sg * 32.0, gy, Z_E)]
    cat += ([(gx0 + sg * 44.0, gy, Z_E + 18.0), (gx0 + sg * 60.0, gy, Z_E + 34.0)] if side == "socket" else [])
    out["Cat 6A cable"] = (poly_tube(cat, 6.5), "cpl_cat6")
    # the LMFB contacts: bridged on the tray (a short loop), wired to the dock's relay on the dock
    if lm:
        (y0_, z0_), (y1_, z1_) = lm
        if side == "socket":
            loop = [(xb, y0_, z0_), (xb - 10.0, y0_, z0_), (xb - 16.0, y0_ - 4.0, Z_E), (xb - 10.0, y1_, z1_), (xb, y1_, z1_)]
            out["LMFB bridge"] = (poly_tube(loop, 1.6), "cpl_wire_sig")
        else:
            for k, (yy, zz) in enumerate(lm):
                out[f"LMFB wire {k}"] = (poly_tube([(xb, yy, zz), (xb + 12.0, yy, zz), (xb + 22.0, yy - 6.0, Z_E + 22.0)],
                                                   1.6), "cpl_wire_sig")
    return out


# ===================================================================================================== the dock
def head_parts(internals=True) -> dict:
    """The dock's moving head at s = 0 (mated), slot frame: the floating panel with the two pin-side frames, the
    plugs, terminations, the float springs, the carriage plate and the guide blocks, the drive pin's ear and the
    lines down to the energy chain."""
    p = {"dock panel": (_panel("pin"), "cpl_alu")}
    for which in FRAMES:
        p.update(_carrier(which, "pin"))
        p.update(_end_pieces(which, "pin"))
    p.update(_couplings("pin", internals))
    p.update(_terminations("pin"))
    xp = X_M + PANEL["half_gap"] + PANEL["t"]           # the dock panel's back: 1237.5
    xc = CARRIAGE_X
    # the float: four shoulder screws through the panel's corners into the carriage plate, each with a spring that
    # holds the panel forward and centres it; the screws pass 4 mm oversize bores in the panel (ours)
    pins, springs = None, None
    for yy in (YC - 80.0, YC + 80.0):
        for zz in (PANEL["z0"] + 10.0, PANEL["z1"] - 10.0):
            sc = xcyl(8.0, xp - 8.0, xc, yy, zz).union(xcyl(13.0, X_M + PANEL["half_gap"] - 4.0,
                                                             X_M + PANEL["half_gap"], yy, zz))
            sp = helix_x(13.0, 1.4, xp + 20.0, xc, yy, zz, 6)
            pins = sc if pins is None else pins.union(sc)
            springs = sp if springs is None else springs.union(sp)
    p["float screws"] = (pins, "cpl_steel")
    p["float springs"] = (springs, "cpl_spring")
    # the carriage plate, hanging from the two guide blocks
    plate = box(xc, YC - 100.0, 22.0, xc + 6.0, YC + 100.0, 131.0)
    plate = plate.cut(box(xc - 1, YC - 52.0, 34.0, xc + 7, YC + 52.0, 112.0))       # lightening window
    ear = box(xc, YC + 96.0, CRANK["z"] - 9.0, xc + 6.0, YC + 140.0, CRANK["z"] + 9.0)
    p["carriage plate"] = (plate.union(ear), "cpl_alu_dark")
    p["drive pin"] = (zcyl(8.0, CRANK["z"] - 9.0, CRANK["z"] + 16.0, xc + 3.0, CRANK["y"]), "cpl_steel")
    blocks = None
    for yr in RAIL_Y:
        b = box(xc - 39.4, yr - 13.5, 131.0, xc + 6.0, yr + 13.5, 141.9)
        blocks = b if blocks is None else blocks.union(b)
    p["guide blocks"] = (blocks, "cpl_steel")
    # the lines: the four tubes leave their fittings, turn down and drop through the bottom plate to the chain's moving
    # end; the cables (mains, Cat 6A, LMFB pair) run along -y behind the panel and drop at the -y side
    tubes = {}
    for y, z, what, medium, key in pole_points("F"):
        c = CPL[what]
        fx = X_M + c["p_body"] + c["p_rear"] + 19.0
        xv = 1286.0
        pts = [(fx, y, z), (xv - 8.0, y, z), (xv, y, z - 8.0), (xv, y, -2.0), (xv, CHAIN["y"] + (y - YC) * 0.5, -10.0)]
        tubes[medium] = pts
        p[f"tube {medium}"] = (poly_tube(pts, c["tube"]), TUBE_MAT[medium])
    xcab = X_M + CARRIER["depth"] + 40.0
    cab = [(xcab, YC - 8.0, Z_E + 26.0), (xcab + 6.0, YC - 30.0, Z_E + 26.0), (xcab + 6.0, YC - 96.0, Z_E + 20.0),
           (xcab + 6.0, YC - 96.0, -4.0), (xcab + 10.0, CHAIN["y"] - 24.0, -10.0)]
    p["mains cable run"] = (poly_tube(cab, 10.5), "cpl_cable")
    _, span = frame_span(E_MODS)
    gy = [(a + b) / 2 for k, a, b, _ in span if k.startswith("CT-10GBIT")][0]
    cat = [(X_M + 34.9 + 32.0, gy, Z_E), (X_M + 34.9 + 38.0, gy, Z_E + 14.0), (X_M + 34.9 + 38.0, YC - 92.0, Z_E + 14.0),
           (X_M + 34.9 + 38.0, YC - 92.0, -4.0), (X_M + 34.9 + 40.0, CHAIN["y"] - 30.0, -10.0)]
    p["Cat 6A run"] = (poly_tube(cat, 6.5), "cpl_cat6")
    # the chain's moving-end bracket, under the head
    p["chain bracket"] = (box(CHAIN["x_end0"] - 6.0, CHAIN["y"] - CHAIN["w"] / 2, -16.0, CHAIN["x_end0"] + 8.0,
                              CHAIN["y"] + CHAIN["w"] / 2, -4.0).union(
        box(CHAIN["x_end0"] - 2.0, CHAIN["y"] - 20.0, -4.0, CHAIN["x_end0"] + 4.0, CHAIN["y"] + 20.0, 20.0)),
        "cpl_alu_dark")
    return p


def dock_fixed() -> dict:
    """The dock's frame, rails, drive motor, end-position sensors and valve bank, slot frame (ours)."""
    d = DOCK
    p = {}
    top = box(d["x0"], d["y0"], d["z1"] - d["t"], d["x1"], d["y1"], d["z1"])
    top = top.cut(box(1290.0, CRANK["y"] - 20.0, d["z1"] - d["t"] - 1, 1340.0, CRANK["y"] + 20.0, d["z1"] + 1))
    bottom = box(1284.0, d["y0"], d["z0"], d["x1"], d["y1"], d["z0"] + d["t"])
    bottom = bottom.cut(box(1280.0, YC - 100.0, d["z0"] - 1, 1384.0, YC + 60.0, d["z0"] + d["t"] + 1))
    back = box(d["x1"] - d["t"], d["y0"], d["z0"], d["x1"], d["y1"], d["z1"])
    sides = box(1282.0, d["y0"], d["z0"], d["x1"], d["y0"] + d["t"], d["z1"]).union(
        box(1282.0, d["y1"] - d["t"], d["z0"], d["x1"], d["y1"], d["z1"]))
    p["dock frame"] = (top.union(bottom).union(back).union(sides), "cpl_alu_dark")
    rails = None
    for yr in RAIL_Y:
        r = box(d["x0"] + 4.0, yr - 6.0, 142.0, d["x1"] - d["t"] - 1.0, yr + 6.0, 150.0)
        rails = r if rails is None else rails.union(r)
    p["guide rails"] = (rails, "cpl_steel")
    # the worm gearmotor over the crank, its output shaft down to the crank; a self-locking worm, 24 V DC (ours)
    cx, cy, cz = CRANK["x"], CRANK["y"], CRANK["z"]
    p["gearbox"] = (box(cx - 22.0, cy - 22.0, cz + 22.0, cx + 22.0, cy + 22.0, cz + 64.0), "cpl_gearbox")
    p["motor"] = (xcyl(36.0, cx + 22.0, cx + 22.0 + 62.0, cy, cz + 43.0).union(
        xcyl(30.0, cx + 22.0 + 62.0, cx + 22.0 + 66.0, cy, cz + 43.0)), "cpl_motor")
    p["gearbox mount"] = (box(cx - 30.0, cy - 30.0, cz + 64.0, cx + 30.0, cy + 30.0, d["z1"] - d["t"]), "cpl_alu_dark")
    p["output shaft"] = (zcyl(10.0, cz + 8.0, cz + 22.0, cx, cy), "cpl_steel")
    # two inductive end-position sensors (M8) on the top plate, looking down at the guide blocks' flag
    for k, xs in enumerate((CARRIAGE_X - 30.0, CARRIAGE_X - 30.0 + STROKE)):
        p[f"sensor {k}"] = (zcyl(8.0, 146.0, d["z1"] + 14.0, xs, RAIL_Y[0] + 24.0), "cpl_sensor")
    # the chain's fixed-end bracket, the chain's tray, and the valve bank under the dock
    p["chain fixed bracket"] = (box(CHAIN["x_fixed"] - 8.0, CHAIN["y"] - CHAIN["w"] / 2, -2 * CHAIN["r"] + CHAIN["z_up"]
                                    - 16.0, CHAIN["x_fixed"] + 6.0, CHAIN["y"] + CHAIN["w"] / 2,
                                    -2 * CHAIN["r"] + CHAIN["z_up"] - 4.0), "cpl_alu_dark")
    p["chain hanger"] = (box(1284.0, CHAIN["y"] - CHAIN["w"] / 2 - 6.0, VALVES_Z[1], 1290.0,
                             CHAIN["y"] + CHAIN["w"] / 2 + 6.0, 0.0), "cpl_alu_dark")
    p.update(valve_bank())
    return p


VALVE_ORDER = ["power", "data", "air", "n2", "cws", "cwr"]


def valve_points() -> dict:
    """{medium: (x, y, z)} of each switching element's indicator on the valve bank, slot frame."""
    out = {}
    for i, key in enumerate(VALVE_ORDER):
        out[key] = (1300.0 + 14.0 * i, YC - 46.0, VALVES_Z[1] + 2.5)
    return out


def valve_bank() -> dict:
    """Under the dock, ours: a DIN rail with the mains contactor and the LMFB relay, an RJ45 coupler, and a manifold of
    four 3/2 solenoid valves (air, N2) and 2/2 valves (water in and out), each with a pressure sensor on its coupling
    side, so the dock knows a line is vented before it lets go."""
    p = {}
    z0, z1 = VALVES_Z
    p["valve bank plate"] = (box(1290.0, YC - 70.0, z0, 1386.0, YC + 70.0, z0 + 6.0), "cpl_alu_dark")
    p["DIN rail"] = (box(1294.0, YC - 66.0, z0 + 6.0, 1382.0, YC - 60.0, z0 + 13.0), "cpl_steel")
    for i, key in enumerate(VALVE_ORDER):
        x = 1300.0 + 14.0 * i
        if key == "power":
            p["contactor"] = (box(x - 6.5, YC - 60.0, z0 + 6.0, x + 6.5, YC - 30.0, z1), "cpl_din")
        elif key == "data":
            p["RJ45 coupler"] = (box(x - 6.0, YC - 60.0, z0 + 6.0, x + 6.0, YC - 34.0, z1 - 20.0), "cpl_din")
        else:
            body = box(x - 5.5, YC - 60.0, z0 + 6.0, x + 5.5, YC - 30.0, z0 + 40.0)
            coil = box(x - 5.5, YC - 58.0, z0 + 40.0, x + 5.5, YC - 32.0, z1)
            p[f"valve {key}"] = (body, "cpl_valve")
            p[f"coil {key}"] = (coil, "cpl_coil")
            p[f"pressure sensor {key}"] = (zcyl(9.0, z0 + 6.0, z0 + 34.0, x, YC + 10.0), "cpl_stainless")
    p["LMFB relay"] = (box(1300.0 + 14.0 * 6 - 6.0, YC - 60.0, z0 + 6.0, 1300.0 + 14.0 * 6 + 6.0, YC - 34.0, z1 - 10.0),
                       "cpl_din")
    return p


def crank_parts() -> dict:
    """The crank arm at phi = 0 (pointing along -x, the head mated), about the axis (CRANK x, y), slot frame."""
    cx, cy, cz = CRANK["x"], CRANK["y"], CRANK["z"]
    r = CRANK["r"]
    arm = cq.Workplane("XY").slot2D(r + 18.0, 18.0).extrude(8.0).translate((cx - r / 2, cy, cz))
    return {"crank": (arm, "cpl_steel"), "crank hub": (zcyl(16.0, cz, cz + 14.0, cx, cy), "cpl_steel")}


def rod_parts() -> dict:
    """The connecting rod lying along x from the crank pin (at phi = 0) to the drive pin, slot frame."""
    cx, cy, cz = CRANK["x"], CRANK["y"], CRANK["z"]
    r, L = CRANK["r"], CRANK["L"]
    x0 = cx - r
    rod = cq.Workplane("XY").slot2D(L + 14.0, 14.0).extrude(6.0).translate((x0 + L / 2, cy, cz + 8.0))
    return {"rod": (rod, "cpl_alu")}


def rod_matrix(phi: float) -> np.ndarray:
    """The rod's pose at crank angle phi, relative to its modelled pose (phi = 0)."""
    cx, cy, cz = CRANK["x"], CRANK["y"], CRANK["z"]
    r, L = CRANK["r"], CRANK["L"]
    ax, ay = cx - r * math.cos(phi), cy - r * math.sin(phi)      # the crank pin (phi = 0: at -x of the axis)
    bx = CARRIAGE_X + 3.0 + drive_s(phi)                          # the drive pin
    ang = math.atan2(cy - ay, bx - ax)                            # the rod's direction
    a0x = cx - r
    m = np.eye(4)
    c, s = math.cos(ang), math.sin(ang)
    m[:2, :2] = [[c, -s], [s, c]]
    m[:3, 3] = (ax - (c * a0x - s * cy), ay - (s * a0x + c * cy), 0.0)
    return m


def crank_matrix(phi: float) -> np.ndarray:
    cx, cy = CRANK["x"], CRANK["y"]
    m = np.eye(4)
    c, s = math.cos(phi), math.sin(phi)
    m[:2, :2] = [[c, -s], [s, c]]
    m[:3, 3] = (cx - (c * cx - s * cy), cy - (s * cx + c * cy), 0.0)
    return m


# ===================================================================================================== the chain
def chain_links(s: float) -> list:
    """[(4x4 pose)] of each link of the energy chain with the head at travel s: upper run from the moving end at
    x_end0 + s along +x to the bend (radius r) at +x, lower run back along -x to the fixed end. The bend moves at half
    the head's speed. Link frame: x along the chain, z out of the bend's centre."""
    c = CHAIN
    xm = c["x_end0"] + s
    xb = (xm + c["x_fixed"] + c["straight"]) / 2.0          # the bend's centre line
    up = xb - xm                                            # upper run's length
    total = c["straight"] + math.pi * c["r"]
    n = int(total // c["pitch"])
    out = []
    for i in range(n):
        t = (i + 0.5) * c["pitch"]
        if t <= up:
            x, z, ang = xm + t, c["z_up"], 0.0
        elif t <= up + math.pi * c["r"]:
            ph = (t - up) / c["r"]
            x, z, ang = xb + c["r"] * math.sin(ph), c["z_up"] - c["r"] + c["r"] * math.cos(ph), ph
        else:
            x, z, ang = xb - (t - up - math.pi * c["r"]), c["z_up"] - 2 * c["r"], math.pi
        m = np.eye(4)
        ca, sa = math.cos(ang), math.sin(ang)
        m[:3, :3] = [[ca, 0, sa], [0, 1, 0], [-sa, 0, ca]]
        m[:3, 3] = (x, c["y"], z)
        out.append(m)
    return out


def chain_mesh(s: float):
    """The chain at travel s as one PolyData: link plates either side and the cross bars, as igus's E2 micro."""
    import pyvista as pv
    c = CHAIN
    meshes = []
    for m in chain_links(s):
        for sy in (-1, 1):
            plate = pv.Box((-c["pitch"] / 2 + 0.6, c["pitch"] / 2 - 0.6, sy * c["w"] / 2 - 2.5, sy * c["w"] / 2 + 2.5 - 0.0,
                            -c["h"] / 2, c["h"] / 2))
            meshes.append(plate.transform(m, inplace=False))
        bar = pv.Box((-3.0, 3.0, -c["w"] / 2, c["w"] / 2, c["h"] / 2 - 3.0, c["h"] / 2))
        meshes.append(bar.transform(m, inplace=False))
    out = meshes[0].merge(meshes[1:]) if len(meshes) > 1 else meshes[0]
    return out.triangulate().extract_surface()


# ===================================================================================================== numbers
def plugging() -> dict:
    """The forces the dock has to give and hold, from the catalogue's per-contact figures (p.135: plugging = 1.5 x the
    sliding force)."""
    n = {"ct3": 0, "pe": 0, "lmfb": 0, "gbit": 0}
    for which in FRAMES:
        for y, z, what, medium, key in pole_points(which):
            if what in n:
                n[what] += 1
    slide = n["ct3"] * SLIDING["ct3"] + n["pe"] * SLIDING["pe"] + n["lmfb"] * SLIDING["lmfb"] + SLIDING["gbit"]
    springs = 2 * CPL["sct"]["spring"] + 2 * CPL["lct"]["spring"]
    plug = 1.5 * slide + springs
    # the crank's torque over the last 15 mm (the contacts' and couplings' engagement): F r sin(phi) / cos(rod angle)
    worst = 0.0
    for k in range(1, 200):
        phi = math.pi * k / 200
        s = drive_s(phi)
        if s > 15.0:
            continue
        r, L = CRANK["r"], CRANK["L"]
        beta = math.asin(r * math.sin(phi) / L)
        torque = plug * r * 1e-3 * abs(math.sin(phi + beta)) / math.cos(beta)
        worst = max(worst, torque)
    return dict(contacts=n, sliding_N=slide, coupling_springs_N=springs, plugging_N=round(plug, 1),
                holding_N=springs, crank_torque_worst_Nm=round(worst, 2),
                note="plugging = 1.5 x the contacts' sliding forces (p.135) plus the four couplings' springs (43 and "
                     "44.5 N without pressure, p.73, p.75); the couplings are vented before mating, so no pressure "
                     "term; the crank's torque is the worst over the last 15 mm of travel, where everything engages")


def clear_mm() -> dict:
    """How far the dock's parts stand from a passing tray, pulled back, and from the cladding."""
    tip_mated = X_M - END["pin_l"]
    return dict(align_pin_tip_mated_x=tip_mated, align_pin_tip_pulled_back_x=tip_mated + STROKE,
                gap_to_tray_side_pulled_back_mm=round(tip_mated + STROKE - SIDE, 1),
                nose_gap_pulled_back_mm=round(X_M - max(PROUD.values()) + STROKE - SIDE, 1),
                dock_to_cladding_mm=round(CLAD_X - DOCK["x1"], 1))


if __name__ == "__main__":
    print(json.dumps(dict(plugging=plugging(), clear=clear_mm(), crank=CRANK, ends=[drive_s(0.0), drive_s(math.pi)]),
                     indent=1))

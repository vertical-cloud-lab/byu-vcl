"""Round 8, the lab stream: the powder-jar store, and the fume hoods without HF (#303, PR #318).

**The jar store.** Sterling (PR #318): "We're going to need a ton of powder jars btw. Easily hundreds, including of
different sizes." Two short trays of labelled jars, each jar standing in a pocket of a rack the arm addresses by seat
(``jar_seats()``), picked from above with the 2F-85's fingers closing front to back:

* **Tray N, feedstock** (``powder_store_feed``): the elements and master alloys DAL buys for its Al alloys (DAL #146:
  Al, Mn, Cr, Zr, Mg, Si, Cu, Ti, Fe, Ni, Ce, Sc, Li as an Al-Li master alloy, Er, Zn, Sn; 100-500 g lots, 100 g per
  atomizer run) in 60, 125, 250 and 500 mL jars, lids coloured by element.
* **Tray O, atomized lots** (``powder_store_lots``): every atomizer run gets a six-character lowercase ID (DAL #157:
  jz31op, 8rthq2, u23y78, c3k0n5, ...) and its sieve fractions (> 250, 150-250, 106-150, 63-106 and < 63 um, as
  ``alloy_print.py``'s turntable splits them) go into 30, 60 and 125 mL jars, each with its run's label.

The jar sizes are typical wide-mouth straight-sided jars, not a supplier's drawing: estimates. The 2F-85 opens 85 mm,
so no jar is wider than 76 mm, and rows are spaced front to back by the jar's diameter plus 20 mm, room for the
fingers to go down beside a jar (6 mm clear of it, 12 mm of finger, 2 mm spare); side by side the jars stand 6 mm
apart.

Round 11 (Sterling, PR #318, 2026-11-13: the jar trays' cameras and UPS are "very inefficient from a vertical space
usage, since the jars are so short. Do we actually need cameras on the jars at all times?"): no. Both trays are passive
(``PASSIVE_TRAYS``): nothing on them draws power or gas, so no UPS, dock plate, tray lines or stream cameras, and the
bay's overhead camera takes the inventory whenever a tray is presented, the only time a jar can come or go. Each rack
now runs the tray's full width, 2410 mm of the 2426 inside the rim (until round 10, 1760 mm, the right end kept for the
UPS, dock and cameras), with 76 mm at each end for its handles, and each slot is as tall as its jars: N 225 mm (was
475), O 150 mm (was 500), both under Shuttle 2's access table. ``python3 r8_store.py json`` writes
``out/powder_store.json``: every seat, its size, what is in it, whether the UR10e reaches it pointing straight down
from the MiR250 parked square to the opening, at the middle and 600 mm either side, and whether the 2F-85, open
around an end seat's lid, clears the rack, its handles, the neighbouring jars and the tray's rim (``gripper_check``).

**The fume hoods, without HF.** Sterling (PR #318): "I don't want to deal with HF in these workflows, especially not with
robotics." Round 7's ducted hood etched a polished Al coupon in Keller's reagent (HF, HCl, HNO3). ``fumehood()`` here is
instruments_r7's with the etch swapped for Weck's reagent (4 g KMnO4 and 1 g NaOH in 100 mL water), an HF-free tint etch
for Al alloys, particularly cast Al-Si (metallographic.com's Weck's page; Springer's two-step colour etch, Metallogr.
Microstruct. Anal. 2012, doi:10.1007/s13632-012-0033-9). ICP-MS goes out to the BYU Spectroscopic Facility's Agilent 8900
ICP-MS/MS (DAL's FLAIME Genesis proposal; labs.chem.byu.edu/byu-spectroscopic-facility/atomic-analysis), which does its
own digestion, so nothing in the lab uses HF. ``fumehood_tray()`` drops round 7's "acids with HF" line. Both keys
replace instruments_r7's in ``tour.load()`` (tour.MODULES: a later module wins).

    python3 r8_store.py json                      # -> out/powder_store.json (the seats, the count, the reach)
    xvfb-run --server-num=16 python3 tour.py powder_store_lots powder_store_feed fumehood fumehood_tray
"""
from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

import cadquery as cq
import numpy as np
import pyvista as pv

import instruments_r7 as R7
import props
from instruments import Instrument, Joint, _piece

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lab_models"))
from common import box  # noqa: E402

MATERIALS = {
    "r8_weck": (0.42, 0.10, 0.40, 0.70, 0.7),        # Weck's reagent: KMnO4, purple
    "r8_rack": (0.86, 0.87, 0.85, 1.0, 0.25),        # white HDPE racks
    "r8_rack_edge": (0.30, 0.45, 0.70, 1.0, 0.3),    # the racks' blue edge strips, one per size band
}

# ===================================================================================================== jars
# size: (body diameter, body height, lid height, mL): typical wide-mouth straight-sided jars (estimates)
JARS = {
    "30 mL": (38.0, 50.0, 12.0, 30),
    "60 mL": (48.0, 60.0, 14.0, 60),
    "125 mL": (58.0, 76.0, 16.0, 125),
    "250 mL": (70.0, 92.0, 18.0, 250),
    "500 mL": (76.0, 150.0, 20.0, 500),
}
# each rack: the tray's full width (2426 mm inside the rim, 8 mm spare each side) and 800 deep (840 inside the rim: a
# passive tray has no power strip along its back); its handles (60 mm wide, 10-70 mm in from each end) and 6 mm to the
# first jar take 76 mm at each end. Round 10: 1760 x 760 mm, left of the UPS
RACK = dict(W=2410.0, D=800.0, h=24.0, pocket=12.0, edge=12.0, handle_zone=76.0)
DX_GAP, DY_GAP = 6.0, 20.0           # side by side; front to back until round 10 (the fingers' room, as was thought)
# Round 11: rows front to back, centre to centre (mm), by the sizes either side. Opened around a cap with 6 mm clear,
# the 2F-85's fingers flare 11 mm (30 mL) to 18 mm (500 mL) past their pads at the cap's height, and higher up its
# linkage is wider still, so a row beside a taller jar needs more room than one beside its own size. From ur_arm's
# meshes with 3 mm spare (round 11's measurement, notes/lab_r8.md); gripper_check re-checks the seats. Until round 10
# every row was the jar's diameter + 20 mm apart, which the fingers cleared for the 30 mL jars only.
ROW_PITCH = {("30 mL", "30 mL"): 61.5, ("60 mL", "60 mL"): 73.5, ("125 mL", "125 mL"): 85.5,
             ("250 mL", "250 mL"): 99.0, ("500 mL", "500 mL"): 103.0, ("30 mL", "60 mL"): 72.5,
             ("60 mL", "125 mL"): 92.0, ("125 mL", "250 mL"): 105.0, ("250 mL", "500 mL"): 116.5}
# each store: [(size, rows)], front to back
LAYOUT = {
    "powder_store_feed": [("60 mL", 2), ("125 mL", 2), ("250 mL", 2), ("500 mL", 2)],
    "powder_store_lots": [("30 mL", 5), ("60 mL", 4), ("125 mL", 2)],
}
# DAL #146's feedstock, with each one's lid colour; Li comes as an Al-Li master alloy (DAL #146: "Li must be bought in
# an Li-Al master alloy to prevent combustion"); Al-Sc, Al-Zr and Al-Er master alloys sit beside the elements
FEED = [("Al", (0.62, 0.66, 0.72)), ("Si", (0.35, 0.36, 0.42)), ("Mg", (0.85, 0.85, 0.80)),
        ("Cu", (0.80, 0.45, 0.25)), ("Mn", (0.55, 0.30, 0.55)), ("Cr", (0.30, 0.55, 0.40)),
        ("Zr", (0.25, 0.35, 0.65)), ("Ti", (0.55, 0.55, 0.60)), ("Fe", (0.55, 0.20, 0.15)),
        ("Ni", (0.25, 0.60, 0.30)), ("Ce", (0.85, 0.70, 0.20)), ("Sc", (0.20, 0.65, 0.70)),
        ("Al-Li", (0.90, 0.30, 0.30)), ("Er", (0.85, 0.50, 0.65)), ("Zn", (0.50, 0.65, 0.85)),
        ("Sn", (0.40, 0.40, 0.30)), ("Al-Sc", (0.15, 0.50, 0.55)), ("Al-Zr", (0.20, 0.25, 0.50))]
FRACTIONS = ["< 63 um", "63-106 um", "106-150 um", "150-250 um", "> 250 um"]
ALLOYS = ["Al 4047", "AlSi10Mg", "Al-10Si", "Al-Mn-Zr", "Al-Ce", "Al-Sc-Zr", "Cu-10Ni", "Al 6063"]
LOT_C = [(0.16, 0.40, 0.75), (0.85, 0.50, 0.15), (0.20, 0.55, 0.30), (0.55, 0.25, 0.60), (0.75, 0.20, 0.25),
         (0.15, 0.55, 0.60), (0.80, 0.70, 0.15), (0.40, 0.42, 0.46)]
DAL_IDS = ["jz31op", "8rthq2", "u23y78", "4yghtr", "9fxeqt", "abc57t", "c3k0n5", "09pol5", "by02uy", "lo7ty1"]
TRAY_PLACEMENT = {"powder_store_feed": dict(tray="N", x=0.0, y=0.0, turn=0.0),
                  "powder_store_lots": dict(tray="O", x=0.0, y=0.0, turn=0.0)}
NEW_TRAYS = {"N": ("2F0", "powder store: feedstock"), "O": ("2F0b", "powder store: atomized lots")}
# round 11: both under Shuttle 2's access table, as vlm.COLUMNS has them (setup_lab.add_slots checks the two agree):
# 3 + 182 + 20 mm for N's 500 mL jars and 3 + 104 + 20 for O's 125 mL ones, up to the 25 mm pitch. Round 10: 2F0 at
# 475 mm and 2R5 at 500, sized for the UPS (437 mm) and the camera posts
NEW_SLOTS = {"2F0": ("front_low", 225.0), "2F0b": ("front_low", 150.0)}
PASSIVE_TRAYS = {"N", "O"}           # no UPS, no dock plate, no cameras (setup_lab.PASSIVE)


def _quiet(c, k=0.35, grey=0.6) -> tuple:
    """A lid colour mixed towards grey: the store reads as rows of jars, not a carpet of colour."""
    return tuple(round(x + (grey - x) * k, 3) for x in c)


FEED = [(el, _quiet(c)) for el, c in FEED]
LOT_C = [_quiet(c) for c in LOT_C]


def _ids(n: int, seed: int = 157) -> list[str]:
    """Six-character lowercase IDs, as DAL #157 labels its runs: its own first, then made-up ones."""
    rnd = random.Random(seed)
    out = list(DAL_IDS)
    while len(out) < n:
        s = "".join(rnd.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(6))
        if s not in out:
            out.append(s)
    return out[:n]


def band_rows(key: str) -> list[dict]:
    """Each size band of a store, front to back: dict(size, ys (its rows' centres), y0, y1 (its rack plate)), in the
    store's frame. Rows ROW_PITCH apart; a plate ends halfway to the next band's first row."""
    D = RACK["D"]
    out, y = [], None
    for size, rows in LAYOUT[key]:
        r = JARS[size][0] / 2 + 1.0                       # the cap's radius
        if y is None:
            y = -D / 2 + RACK["edge"] + r + 4.0
        else:
            y += ROW_PITCH[(out[-1]["size"], size)]
        ys = [y + ROW_PITCH[(size, size)] * i for i in range(rows)]
        y = ys[-1]
        out.append(dict(size=size, ys=ys, r=r))
    for i, b in enumerate(out):
        b["y0"] = -D / 2 if i == 0 else (out[i - 1]["ys"][-1] + b["ys"][0]) / 2
        b["y1"] = b["ys"][-1] + b["r"] + 8.0 if i == len(out) - 1 else (b["ys"][-1] + out[i + 1]["ys"][0]) / 2
    assert out[-1]["y1"] - out[0]["y0"] <= D + 1e-6, (key, out[0]["y0"], out[-1]["y1"])
    dy = -(out[0]["y0"] + out[-1]["y1"]) / 2       # centred front to back: the frame's origin is the store's middle,
    for b in out:                                  # where setup_lab.placed() puts it on the tray
        b["ys"] = [y + dy for y in b["ys"]]
        b["y0"], b["y1"] = b["y0"] + dy, b["y1"] + dy
    return out


def jar_seats(key: str) -> list[dict]:
    """Every seat of a store, in its own frame (the rack's centre, y to the back): dict(size, x, y, z (the jar's base),
    row, col, content, label, lid colour)."""
    W = RACK["W"]
    seats = []
    lots = _ids(80)
    li = 0
    fi = 0
    for band, (bd, (size, rows)) in enumerate(zip(band_rows(key), LAYOUT[key])):
        d, h, lid, ml = JARS[size]
        px = d + DX_GAP
        ncol = int((W - 2 * RACK["handle_zone"] + DX_GAP) // px)      # n jars take n * px - DX_GAP
        x0 = -(ncol - 1) * px / 2
        for r in range(rows):
            yc = bd["ys"][r]
            for c in range(ncol):
                if key == "powder_store_feed":
                    el, col = FEED[fi % len(FEED)]
                    fi += 1
                    content, label = f"{el} powder" if "-" not in el else f"{el} master alloy", el
                else:
                    run = lots[li // len(FRACTIONS) % len(lots)]
                    frac = FRACTIONS[li % len(FRACTIONS)]
                    a = ALLOYS[(li // len(FRACTIONS)) % len(ALLOYS)]
                    col = LOT_C[(li // len(FRACTIONS)) % len(LOT_C)]
                    li += 1
                    content, label = f"{a}, {frac}", f"{run} {frac}"
                seats.append(dict(size=size, ml=ml, x=round(x0 + c * px, 1), y=round(yc, 1),
                                  z=RACK["h"] - RACK["pocket"], row=r, band=band, col=c, content=content, label=label, lid=col))
    return seats


def _cyl_mesh(r, h, z0, res=28):
    return pv.Cylinder(center=(0, 0, z0 + h / 2), direction=(0, 0, 1), radius=r, height=h, resolution=res).triangulate()


def _merged(mesh, pts):
    out = [mesh.translate(tuple(p), inplace=False) for p in pts]
    return out[0].merge(out[1:]) if len(out) > 1 else out[0]


# what a clip tints, with its legend (props.TINT names): feedstock, the master alloys and the two elements of Al 4047
# (Al-12Si); lots, the < 63 um LPBF cut and the other cuts of run jz31op
TINT_LEGEND = {"powder_store_feed": [("amber", "Al master alloys (Al-Li, Al-Sc, Al-Zr)"), ("teal", "Al and Si: Al 4047's elements")],
               "powder_store_lots": [("amber", "< 63 um: the LPBF cut"), ("teal", "run jz31op, its other cuts")]}


def _tint_of(key: str, s: dict) -> str | None:
    if key == "powder_store_feed":
        if s["label"].startswith("Al-"):
            return "amber"
        return "teal" if s["label"] in ("Al", "Si") else None
    if s["label"].endswith(FRACTIONS[0]):
        return "amber"
    return "teal" if s["label"].startswith("jz31op") else None


def store(key: str) -> Instrument:
    seats = jar_seats(key)
    feed = key == "powder_store_feed"
    W, D = RACK["W"], RACK["D"]
    hmax = max(JARS[s["size"]][1] + JARS[s["size"]][2] for s in seats) + RACK["h"] - RACK["pocket"]
    title = "Powder-jar store: feedstock" if feed else "Powder-jar store: atomized lots"
    inst = Instrument(key, title, "Jar racks on a tray (our design)", (W, D, round(hmax)),
                      "Our design: DAL #146's feedstock and DAL #157's run IDs; wide-mouth jars at typical sizes "
                      "(estimates)")
    body = _piece(inst, "body")
    # one rack per size band: a plate with a round pocket per jar, and a blue edge strip along its front
    bands = {}
    for s in seats:
        bands.setdefault(s["band"], []).append(s)
    brows = band_rows(key)
    for b, ss in bands.items():
        d = JARS[ss[0]["size"]][0]
        y0, y1 = brows[b]["y0"], brows[b]["y1"]
        plate = box(-W / 2, y0 + 2, 0, W / 2, y1 - 2, RACK["h"])
        cut = cq.Workplane("XY").pushPoints([(s["x"], s["y"]) for s in ss]).circle(d / 2 + 1.5) \
            .extrude(RACK["pocket"] + 1).translate((0, 0, RACK["h"] - RACK["pocket"]))
        body.add(f"rack {ss[0]['size']} {b}", plate.cut(cut), "r8_rack")
        body.add(f"rack edge {b}", box(-W / 2, y0 + 2, RACK["h"] - 6, W / 2, y0 + 8, RACK["h"]), "r8_rack_edge")
        for sx in (-1, 1):                 # handles at each end, 6 mm past the end jars: a person lifts a rack out whole
            hx = sx * (W / 2 - 40)
            body.add(f"rack handle {b} {sx}", box(hx - 30, (y0 + y1) / 2 - 8, RACK["h"], hx + 30, (y0 + y1) / 2 + 8,
                                                  RACK["h"] + 30).cut(box(hx - 20, (y0 + y1) / 2 - 9, RACK["h"],
                                                                          hx + 20, (y0 + y1) / 2 + 9,
                                                                          RACK["h"] + 20)), "r7_frame")
    # round 9 (Sterling: "Keep them all a normal black lid with transparent glass"): every jar is props.py's lab-wide
    # jar, clear glass with a black cap, a white label and the powder showing. What a clip points out is a tint on just
    # those jars (a see-through sleeve in the "jar tint" piece), shown with a legend for a few seconds, then faded back.
    by_size: dict[str, list] = {}
    for s in seats:
        by_size.setdefault(s["size"], []).append(s)
    inst.meshes["body"] = []
    tints: dict[tuple, list] = {}
    for size, ss in by_size.items():
        d, h, lid, _ = JARS[size]
        for part, (m, rgb, op) in props.jar_parts(d, h, lid).items():
            inst.meshes["body"].append((_merged(m, [(s["x"], s["y"], s["z"]) for s in ss]), rgb, op))
        for s in ss:
            t = _tint_of(key, s)
            if t:
                tints.setdefault((size, t), []).append((s["x"], s["y"], s["z"]))
    _piece(inst, "jar tint").add("tint anchor", box(-0.5, -0.5, -0.5, 0.5, 0.5, 0.5), "r8_rack")   # hidden, 1 mm
    inst.meshes["jar tint"] = [(_merged(props.tint_sleeve(*JARS[size][:2]), pts), props.TINT[t], props.TINT_OPACITY)
                               for (size, t), pts in tints.items()]
    inst.joints["jar tint"] = Joint("fade")
    n = len(seats)
    sizes = ", ".join(f"{len(v)} x {k}" for k, v in by_size.items())
    if feed:
        inst.actions = [
            (f"Tray N, the feedstock: {n} labelled jars ({sizes}) in racks of white HDPE, one rack per size.", 3.0, {}),
            ("DAL's elements and master alloys (DAL #146: Al, Si, Mg, Cu, Mn, Cr, Zr, Ti, Fe, Ni, Ce, Sc, Er, Zn, Sn, "
             "Li as Al-Li), each in clear glass with a black cap; 100 g goes into each atomizer run.", 3.4, {}),
            ("Tinted for now (legend, top right): the master alloys and the two elements of Al 4047.", 1.8,
             {"jar tint": (0.0, 1.0)}),
            ("The tint is only a highlight, held for a few seconds...", 2.2, {"jar tint": (1.0, 1.0)}),
            ("...then it fades back: every jar is the same clear glass with a black cap.", 1.8,
             {"jar tint": (1.0, 0.0)}),
            ("Rows stand 21-41 mm apart front to back, room for the gripper's open fingers; the arm takes a jar from "
             "above.", 3.0, {}),
            ("Each rack runs the tray's full width and lifts out whole by its handles. Nothing here draws power: no "
             "UPS, no cameras. The bay's overhead camera counts the jars whenever the tray is presented.", 2.6, {}),
        ]
        inst.zoom = {1: ((-500.0, -250.0, 60.0), 900.0), 5: ((300.0, -150.0, 60.0), 700.0), 6: "out"}
        br = {b["size"]: b for b in band_rows(key)}      # round 11: on each band's first row, as the rows now stand
        inst.labels = [(sz, (x, br[sz]["ys"][0], RACK["h"] - RACK["pocket"] + JARS[sz][1] + JARS[sz][2]), at)
                       for sz, x, at in (("60 mL", -700.0, (0.10, 0.82)), ("125 mL", -300.0, (0.30, 0.86)),
                                         ("250 mL", 100.0, (0.55, 0.86)), ("500 mL", 500.0, (0.82, 0.80)))]
    else:
        inst.actions = [
            (f"Tray O, the atomized lots: {n} labelled jars ({sizes}). Every run gets a six-character ID (DAL #157: "
             "jz31op, 8rthq2, c3k0n5, ...).", 3.4, {}),
            ("Each run's sieve fractions go in jars of their own: < 63 um for LPBF, 63-106, 106-150, 150-250 and "
             "> 250 um.", 3.2, {}),
            ("Clear glass, a black cap, a white label with the run and fraction.", 2.4, {}),
            ("Tinted for now (legend, top right): the < 63 um LPBF cut, and the other cuts of run jz31op.", 1.8,
             {"jar tint": (0.0, 1.0)}),
            ("Only a highlight, held for a few seconds...", 2.0, {"jar tint": (1.0, 1.0)}),
            ("...then back to plain glass and black caps.", 1.8, {"jar tint": (1.0, 0.0)}),
            ("The arm picks by seat: out/powder_store.json lists every jar, what is in it and whether the arm reaches "
             "it.", 3.0, {}),
        ]
        inst.zoom = {1: ((-600.0, -300.0, 50.0), 800.0), 2: ((200.0, -120.0, 60.0), 650.0), 6: "out"}
        br = {b["size"]: b for b in band_rows(key)}
        c3 = next(st for st in seats if st["label"] == "c3k0n5 < 63 um")   # round 8 pointed at seats[6], 8rthq2's
        inst.labels = [("30 mL: c3k0n5 < 63 um", (c3["x"], c3["y"] - 20, 60), (0.10, 0.80)),
                       ("60 mL", (0, br["60 mL"]["ys"][0], 86), (0.45, 0.86)),
                       ("125 mL", (400, br["125 mL"]["ys"][0], 104), (0.80, 0.80))]
    inst.cam = (0.25, -1.5, 0.80)          # low enough to see the labels on the jars' sides
    inst.framing = (0.56, 0.30)
    inst.notes = [f"{n} jars: {sizes}", "jar sizes are typical wide-mouth jars: estimates"]
    return inst


def powder_store_feed() -> Instrument:
    return store("powder_store_feed")


def powder_store_lots() -> Instrument:
    return store("powder_store_lots")


# ===================================================================================================== fume hoods
def fumehood() -> Instrument:
    """instruments_r7's ducted XStream with the etch HF-free: Weck's reagent in place of Keller's."""
    inst = R7.fumehood()
    for m in inst.pieces.values():
        for p in m.parts:
            if p.material == "r7_keller":
                p.material = "r8_weck"
    inst.model = "Labconco Protector XStream 4 ft"
    inst.actions = [
        ("The sash rises to its stop, 457 mm (18 in) open. The arm works through that opening, as a person does.",
         2.2, inst.actions[0][2]),
        ("Air sweeps in under the sash, over the airfoil, through the baffle's slots and up the 325 mm collar to the "
         "building's exhaust.", 3.2, inst.actions[1][2]),
        ("A polished Al coupon goes into Weck's reagent (KMnO4 and NaOH in water) for a few seconds: an HF-free tint "
         "etch for Al alloys.", 3.0, inst.actions[2][2]),
        ("Then into the rinse water, while the hood keeps pulling.", 3.0, inst.actions[3][2]),
        ("Sash down. Nothing here uses HF: ICP-MS goes out to the BYU Spectroscopic Facility's Agilent 8900. 1219 mm "
         "wide, 2.4 m tall with its base: it stands on the floor.", 2.6, inst.actions[4][2]),
    ]
    inst.labels = [(("Weck's reagent (no HF)",) + tuple(lb[1:])) if lb[0] == "Keller's reagent" else lb
                   for lb in inst.labels]
    return inst


def fumehood_tray() -> Instrument:
    inst = R7.fumehood_tray()
    last = inst.actions[-1]
    inst.actions[-1] = ("660 x 610 x 635 mm and 41 kg: it fits a tray, 715 mm with the hose. Carbon takes solvent "
                        "vapours; the etch goes to the ducted hood, and nothing in the lab uses HF.", last[1], last[2])
    return inst


for _k, _items in TINT_LEGEND.items():
    R7.PLOTS[f"instruments/{_k}"] = props.piece_legend(
        _k, {"jar tint": ("Tinted for now", [(props.TINT[c], t) for c, t in _items])})

REGISTRY = {"powder_store_feed": powder_store_feed, "powder_store_lots": powder_store_lots,
            "fumehood": fumehood, "fumehood_tray": fumehood_tray}


# ===================================================================================================== the count
def reach(seats, tray_lift=0.0, offsets=(-600.0, 0.0, 600.0)) -> list:
    """For each seat (the store at TRAY_PLACEMENT on its tray, the tray at the opening), the MiR offsets along the
    opening from which the UR10e reaches the jar's lid pointing straight down, its fingers closing front to back."""
    import animate as A
    import props as P
    import reach as RH
    import ur_arm
    import vlm as V
    from scene import T
    seeds = [np.radians(q) for q in ((-90, -100, 110, -100, -90, 0), (-60, -80, 100, -110, -90, 0),
                                     (-120, -80, 100, -110, -90, 0), (-90, -60, 60, -90, -90, 0))]
    out = []
    for s in seats:
        jar = JARS[s["size"]]
        grip_z = s["z"] + jar[1] + jar[2] * 0.5          # the lid's middle
        p = np.array([s["x"] + s["tx"], V.Y_OPEN + s["y"] + s["ty"], V.Z_OPEN + V.T_FLOOR + grip_z])
        ok = []
        for dx in offsets:
            Tw = T((-dx, 0, 0)) @ P.tcp_frame(p, (0, 0, -1), 0.0)
            q = RH.solve(A.ROBOT, Tw, seeds)
            if q is not None:
                ok.append(dx)
        out.append(ok)
    return out


def _pad_gap(close: float) -> float:
    """The 2F-85's pad faces' distance apart (mm) at a closure (ur_arm.gripper_fk, ur_arm._PAD)."""
    import ur_arm
    G = ur_arm.gripper_fk(close)
    a = G["left_finger_tip"] @ np.array([-ur_arm._PAD[0], 0.0, ur_arm._PAD[1], 1.0])
    b = G["right_finger_tip"] @ np.array([ur_arm._PAD[0], 0.0, ur_arm._PAD[1], 1.0])
    return float(np.linalg.norm((a - b)[:3]))


def _close_for(gap: float) -> float:
    lo, hi = 0.0, 1.0                    # the gap shrinks as it closes
    if gap >= _pad_gap(0.0):
        return 0.0
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if _pad_gap(mid) > gap else (lo, mid)
    return (lo + hi) / 2


def gripper_check(key: str, clear: float = 6.0) -> dict:
    """Round 11: can the 2F-85 take the seats at a rack's ends, beside its handles and the tray's side rims? The
    gripper is opened around the seat's cap (its pads `clear` mm off it, or as wide as it opens), its grasp point at the
    cap's middle and its fingers closing front to back (along y), turned either way about the vertical (the wrist D405
    on one side or the other). Its meshes (ur_arm.gripper_meshes: adapter, base, knuckles, fingers, the D405 on its
    bracket) against the rack plates and their handles as solid boxes, every jar near it (glass and cap as cylinders)
    and the tray's rim (vlm.tray's 12 mm walls, 53 mm tall at the back and sides, 15 mm at the front): FCL, in the
    tray's frame. Checked: each row's two end seats and its middle one. Straight down from above, so the pose at the
    bottom is the tightest one on the way in. -> {"seats": [...], "all_clear": bool}"""
    import fcl
    import pyvista as pv
    import props as P
    import ur_arm
    import vlm as V
    seats = jar_seats(key)
    pl = TRAY_PLACEMENT[key]
    W = RACK["W"]
    z0 = V.T_FLOOR
    fixed = []

    def box_obj(name, x0, x1, y0, y1, za, zb):
        tf = fcl.Transform(np.array([(x0 + x1) / 2, (y0 + y1) / 2, (za + zb) / 2]))
        fixed.append((name, fcl.CollisionObject(fcl.Box(x1 - x0, y1 - y0, zb - za), tf), (x0, x1, y0, y1)))
    for bd in band_rows(key):
        y0, y1 = bd["y0"] + pl["y"], bd["y1"] + pl["y"]
        box_obj(f"rack {bd['size']}", pl["x"] - W / 2, pl["x"] + W / 2, y0 + 2, y1 - 2, z0, z0 + RACK["h"])
        for sx in (-1, 1):
            hx = pl["x"] + sx * (W / 2 - 40)
            box_obj(f"handle {bd['size']} {'right' if sx > 0 else 'left'}", hx - 30, hx + 30, (y0 + y1) / 2 - 8,
                    (y0 + y1) / 2 + 8, z0 + RACK["h"], z0 + RACK["h"] + 30)
    xo, yo, xi, yi = V.TRAY_W / 2, V.TRAY_D / 2, V.TRAY_W / 2 - 12, V.TRAY_D / 2 - 12
    hz = V.T_FLOOR + V.T_RIM
    box_obj("tray rim, left", -xo, -xi, -yo, yo, 0.0, hz)
    box_obj("tray rim, right", xi, xo, -yo, yo, 0.0, hz)
    box_obj("tray rim, back", -xo, xo, yi, yo, 0.0, hz)
    box_obj("tray rim, front lip", -xo, xo, -yo, -yi, 0.0, V.T_FLOOR + 12)
    jars = []
    for i, st in enumerate(seats):
        d, h, lid, _ = JARS[st["size"]]
        x, y, zb = st["x"] + pl["x"], st["y"] + pl["y"], z0 + st["z"]
        jars.append((i, x, y, fcl.CollisionObject(fcl.Cylinder(d / 2, h), fcl.Transform(np.array([x, y, zb + h / 2]))),
                     fcl.CollisionObject(fcl.Cylinder(d / 2 + 1.0, lid),
                                         fcl.Transform(np.array([x, y, zb + h + lid / 2])))))
    gm = ur_arm.gripper_meshes()
    cache = {}

    def gripper(close):
        if close not in cache:
            G = ur_arm.gripper_fk(close)
            ms = [m.transform(G[part], inplace=False) for part, lst in gm.items() for m, _, _ in lst]
            mesh = pv.merge(ms).triangulate()
            tris = mesh.faces.reshape(-1, 4)[:, 1:]
            bvh = fcl.BVHModel()
            bvh.beginModel(mesh.n_points, len(tris))
            bvh.addSubModel(np.asarray(mesh.points, float), np.asarray(tris, np.int32))
            bvh.endModel()
            cache[close] = bvh
        return cache[close]
    out, rows = [], {}
    for i, st in enumerate(seats):
        rows.setdefault((st["band"], st["row"]), []).append(i)
    for (band, row), idx in sorted(rows.items()):
        idx = sorted(idx, key=lambda j: seats[j]["x"])
        for which, j in (("left end", idx[0]), ("middle", idx[len(idx) // 2]), ("right end", idx[-1])):
            st = seats[j]
            d, h, lid, _ = JARS[st["size"]]
            gap = min(d + 2.0 + 2 * clear, _pad_gap(0.0))
            close = round(_close_for(gap), 4)
            x, y = st["x"] + pl["x"], st["y"] + pl["y"]
            p = np.array([x, y, z0 + st["z"] + h + lid / 2])
            res = {}
            for spin in (90.0, -90.0):
                Tw = P.tcp_frame(p, (0, 0, -1), spin)          # spin +-90: the fingers close along y
                M = Tw @ np.diag([1.0, 1.0, 1.0, 1.0])
                M[:3, 3] = (Tw @ np.array([0.0, 0.0, -ur_arm.tcp_mm(close), 1.0]))[:3]
                g = fcl.CollisionObject(gripper(close), fcl.Transform(M[:3, :3], M[:3, 3]))
                near = [(nm, o) for nm, o, (bx0, bx1, by0, by1) in fixed
                        if bx0 - 200 < x < bx1 + 200 and by0 - 200 < y < by1 + 200]
                near += [(f"jar {jj} ({seats[jj]['size']}{', the one it takes' if jj == j else ''})", o)
                         for jj, jx, jy, ob, oc in jars if abs(jx - x) < 160 and abs(jy - y) < 160 for o in (ob, oc)]
                hits, dmin = [], {}
                for nm, o in near:
                    r = fcl.DistanceResult()
                    dist = fcl.distance(g, o, fcl.DistanceRequest(), r)
                    kind = "taken jar" if "the one it takes" in nm else nm.split(" ")[0]
                    dmin[kind] = round(min(dmin.get(kind, 1e9), float(dist)), 1)
                    if dist <= 0.0:
                        hits.append(nm)
                res[f"spin {spin:+.0f}"] = dict(hits=sorted(set(hits)), min_clearance_mm=dmin)
            ok = any(not v["hits"] for v in res.values())
            out.append(dict(size=st["size"], band=band, row=row, which=which, x=round(x, 1), y=round(y, 1),
                            pad_gap_mm=round(gap, 1), close=close, clear=ok, poses=res))
    return dict(seats=out, all_clear=all(o["clear"] for o in out),
                method="the 2F-85 (ur_arm meshes, the D405 included) open around the cap, its grasp point at the cap's "
                       "middle, fingers closing along y; FCL distance to the rack plates and handles (boxes), the jars "
                       "near it (cylinders) and the tray's rim, in the tray's frame; clear if either spin (+-90) is")


def write_json(path=None) -> dict:
    path = Path(path or HERE / "out" / "powder_store.json")
    res = dict(sources={
        "DAL #146 (feedstock)": "https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/146",
        "DAL #157 (run IDs, labels)": "https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/157",
        "jar sizes": "typical wide-mouth straight-sided jars: estimates, not a supplier's drawing"},
        jar_sizes_mm={k: dict(diameter=v[0], body_h=v[1], lid_h=v[2], ml=v[3]) for k, v in JARS.items()},
        spacing_mm=dict(side_by_side=DX_GAP, front_to_back=DY_GAP), stores={})
    total = 0
    for key, pl in TRAY_PLACEMENT.items():
        seats = jar_seats(key)
        for s in seats:
            s["tx"], s["ty"] = pl["x"], pl["y"]
        try:
            rch = reach(seats)
        except Exception as e:                        # noqa: BLE001  (the count stands without the reach)
            print("reach not checked:", e, flush=True)
            rch = [None] * len(seats)
        by = {}
        for s, r in zip(seats, rch):
            b = by.setdefault(s["size"], dict(n=0, reach_centre=0, reach_any=0))
            b["n"] += 1
            if r:
                b["reach_any"] += 1
                b["reach_centre"] += 0.0 in r
        total += len(seats)
        try:
            grip = gripper_check(key)
        except Exception as e:                        # noqa: BLE001  (the count stands without it)
            print("gripper not checked:", e, flush=True)
            grip = None
        res["stores"][key] = dict(tray=pl["tray"], slot=NEW_TRAYS[pl["tray"]][0],
                                  slot_span_mm=NEW_SLOTS[NEW_TRAYS[pl["tray"]][0]][1], rack_mm=[RACK["W"], RACK["D"]],
                                  jars=len(seats), by_size=by, gripper_end_seats=grip,
                                  reach_from_centre=sum(b["reach_centre"] for b in by.values()),
                                  reach_from_any_of_three=sum(b["reach_any"] for b in by.values()),
                                  seats=[dict(size=s["size"], x=s["x"], y=s["y"], content=s["content"],
                                              label=s["label"], reach_offsets_mm=r) for s, r in zip(seats, rch)])
    res["total_jars"] = total
    res["note"] = ("reach: the UR10e on the MiR250 parked square to the opening (animate.AMR_XY), the gripper pointing "
                   "straight down at the lid's middle, fingers closing front to back; MiR offsets of -600, 0 and +600 "
                   "mm along the opening. IK only (ur_arm.ik via reach.solve): no collision check")
    path.write_text(json.dumps(res, indent=1) + "\n")
    return res


if __name__ == "__main__":
    if sys.argv[1:2] == ["json"]:
        r = write_json()
        print("total jars", r["total_jars"])
        for k, v in r["stores"].items():
            print(k, v["tray"], v["slot"], v["jars"], {s: b["n"] for s, b in v["by_size"].items()},
                  "reach centre", v["reach_from_centre"], "any", v["reach_from_any_of_three"])
            g = v["gripper_end_seats"]
            if g:
                print("  gripper at the end seats:", "all clear" if g["all_clear"] else "CHECK")
                for o in g["seats"]:
                    print("   ", o["size"], "row", o["row"], o["which"].ljust(9), "clear" if o["clear"] else "HIT",
                          {sp: (v2["hits"], v2["min_clearance_mm"]) for sp, v2 in o["poses"].items()})

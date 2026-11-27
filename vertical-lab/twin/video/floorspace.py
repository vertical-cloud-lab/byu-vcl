"""Floor space: the vertical lab's equipment laid out three ways, and each layout's area computed from its footprints,
clearances and aisles. A design comparison: none of these labs is built.

    cd vertical-lab
    python -m twin.video.floorspace            # -> out/floorspace/layouts.json, out/floorspace/plans.png, the table

The equipment is the 3-D lab's (PR 318's scene, which the campaign video's replay drives): every instrument on its
trays, as setup_lab.py fit measured it (out/tray_plan.json, the tray's frame), and every floor machine, measured from
the built scene (out/twin2/video/birdseye/high.json "bounds"). The same list goes into all three layouts:

1. conventional(): a materials lab laid out the usual way, grouped by workflow along a central corridor. Rooms where
   a materials lab has them (a powder and melt room, a metal AM bay, a machine shop, a furnace room, an SEM room),
   open lab and a mechanical-testing area for the rest. Benchtop instruments stand on benches; floor machines get
   service clearance behind and beside them; every row faces a 5 ft aisle.
2. flat(): the same plan, the same walls, automated: MiR250 + UR12e mobile manipulators drive the routes people
   walked, a fixed arm stands at each bench cluster, and every station gets a docking target and a sample rack.
3. vertical(): the two Kardex Shuttles take every benchtop instrument on its tray (the tray plan), and the floor
   machines stand in two rows along one MiR aisle, as the 3-D lab has them, packed by the same clearance rules.

The rules are ASSUME's, each with its source or marked as our choice. An area is the outer rectangle of the layout's
walls, so it counts the walls, the corridor, every aisle and every clearance: what a floor plan would be billed as.
"""
from __future__ import annotations

import heapq
import json
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[2]            # vertical-lab/
OUTD = HERE / "out" / "floorspace"
SQFT_PER_M2 = 10.763910417

# ============================================================================================ assumptions (mm)
ASSUME = dict(
    bench_d=762.0,          # 30 in bench (NIH ORF, "Lab Module Design Considerations", Technical Bulletin 23, Dec 2013)
    bench_d_deep=914.0,     # 36 in, for an instrument deeper than 712 mm (equipment up to 36 in: the same bulletin)
    bench_h=914.0,          # 36 in standing height (our choice; a common casework height)
    bench_gap=150.0,        # between instruments on a bench and at its ends (our choice: vents and cables)
    bench_module=305.0,     # bench runs come in whole feet (casework widths; our choice)
    bench_back=50.0,        # an instrument's back off the bench's back edge
    aisle=1524.0,           # 5 ft between rows: NIH's bulletin (the ADA turning radius; back-to-back work)
    corridor=1829.0,        # 6 ft main corridor (our choice; the building code's minimum is 44 in, 1118 mm)
    service=600.0,          # behind and beside a floor machine (our choice; a technician kneels there)
    wall=150.0,             # partition and outer walls
    door=1219.0,            # a 4 ft equipment door, with 150 mm of wall either side
    mir_aisle=3000.0,       # the vertical lab's aisle: two MiR250s pass (MiR250 spec sheet, 2023-06-28)
    mir_corridor=1450.0,    # one MiR250 driving (the same sheet)
    dock_zone=838.0,        # from a row's fronts to the aisle's edge in the 3-D lab (-1562 to -2400)
    shelf_h=1830.0,         # storage shelving, 6 ft (our choice)
    module=3353.0,          # no room narrower than one 11 ft lab module (NIH's bulletin: 11 ft is the ideal module)
)

# ============================================================================================ the equipment
# tray item name (setup_lab fit's "item") -> (short label, workflow group, counts as an instrument)
ITEM_INFO = {
    "Hitachi TM4000PlusII": ("SEM (Hitachi TM4000Plus II)", "sem", True),
    "Rigaku MiniFlex (6th generation)": ("XRD (Rigaku MiniFlex)", "analytical", True),
    "Powder prep station: XRD holder, SEM stub, XRF cup (our design)": ("powder prep station", "analytical", True),
    "Opentrons OT-2": ("Opentrons OT-2", "wet", True),
    "CubXL + NuVant EZstat Pro": ("corrosion cell (CubXL + EZstat)", "wet", True),
    "vial rack": ("vial rack", "powder", False),
    "multi-doser: chain carousel v5 on an HR-202i, 13 powders": ("multi-doser", "powder", True),
    "Specac Atlas Autotouch 15T, vacuum press": ("vacuum press (Specac)", "powder", True),
    "Plastometrex PLX-Benchtop": ("PIP (Plastometrex)", "mech", True),
    "KLA iMicro": ("nanoindenter (KLA iMicro)", "mech", True),
    "Malvern Mastersizer 3000 + Aero S": ("particle size (Mastersizer)", "analytical", True),
    "Storage load (our design)": ("sample store", "store", False),
    "Bambu Lab H2D": ("Bambu Lab H2D", "fab", True),
    "Bambu Lab A1 mini": ("Bambu Lab A1 mini", "fab", True),
    "LECO PX500 + disc magazine": ("polisher (LECO PX500)", "prep", True),
    "Nabertherm NAT 15/65": ("furnace (Nabertherm)", "furnace", True),
    "LECO MX400": ("mounting press (LECO MX400)", "prep", True),
    "six-shelf disc magazine (ours)": ("disc magazine", "prep", False),
    "water tank with a lift basket, our design": ("quench tank", "furnace", False),
    "Custom N2 glovebox (purge-only)": ("N2 glovebox", "powder", True),
    "Keyence VHX-7000 (VHX-S750E free-angle stand)": ("digital microscope (Keyence VHX)", "sem", True),
    "ZwickRoell zwickiLine Z5.0 TN": ("tensile (zwickiLine)", "mech", True),
    "Mitutoyo HM-220 Type D (AVPAK)": ("hardness (Mitutoyo HM-220)", "mech", True),
    "Bruker S2 PUMA Series 2, XY Autochanger": ("XRF (Bruker S2 PUMA)", "analytical", True),
    "Sentry Air Systems ductless hood, 24 in": ("ductless hood", "shop", True),
    "Makera Carvera": ("CNC (Makera Carvera)", "shop", True),
    "DDM Novastar SPR-45VA": ("stencil printer", "fab", True),
    "Opulo LumenPnP v4.2": ("pick-and-place (LumenPnP)", "fab", True),
    "Puhui T-962A": ("reflow oven", "fab", True),
    "Formlabs Form 4": ("Formlabs Form 4", "fab", True),
    "Formlabs Form Wash (2nd Gen)": ("Form Wash", "fab", True),
    "Formlabs Form Cure (2nd Gen)": ("Form Cure", "fab", True),
    "SnowX SnowPod": ("desktop LPBF (SnowPod)", "powder", True),
    "264 powder jars in racks (our design)": ("powder jars, feedstock", "jars", False),
    "489 powder jars in racks (our design)": ("powder jars, atomized lots", "jars", False),
}
# floor machine (the scene's key) -> (label, workflow group, its front's facing in the 3-D lab)
FLOOR_INFO = {
    "repowder": ("atomizer (AMAZEMET rePowder)", "powder", "S"),
    "sieve_cell": ("sieving cell", "powder", "S"),
    "glovebox": ("glovebox (Ar)", "powder", "S"),
    "aconity": ("LPBF (Aconity MIDI)", "am", "S"),
    "ded": ("DED (MX-Lab)", "am", "N"),
    "eos_m400": ("LPBF (EOS M 400-4)", "am", "N"),
    "meltio_cell": ("DED cell (Meltio)", "am", "N"),
    "wire_edm": ("wire EDM (FANUC)", "shop", "N"),
    "instron_floor": ("tensile (Instron 68FM-100)", "mech", "N"),
    "instron_small": ("tensile (Instron 68SC-2)", "mech", "N"),
    "fumehood": ("fume hood", "wet", "N"),
    "packaging": ("packaging station", "ship", "S"),
}
FACING = {"E": 0.0, "N": 90.0, "W": 180.0, "S": -90.0}


def _load_tray_plan() -> dict:
    return json.loads((HERE / "out" / "tray_plan.json").read_text())


def _load_floor_bounds() -> dict:
    js = json.loads((HERE / "out" / "twin2" / "video" / "birdseye" / "high.json").read_text())
    return js["bounds"]


@dataclass
class Item:
    """One piece of equipment: a benchtop item from a tray (tray, idx: its place in the tray's item list) or a floor
    machine (tray None)."""
    key: str                       # unique: tray + index ("D0") or the floor machine's key
    name: str                      # the scene's name
    label: str
    group: str
    instrument: bool
    w: float                       # along its front, mm
    d: float                       # front to back
    h: float
    tray: str | None = None
    idx: int | None = None
    box: tuple | None = None       # the tray-frame box (x0, x1, y0, y1, z0, z1)
    facing0: str = "S"             # the 3-D lab's facing (floor machines)
    rect0: tuple | None = None     # the 3-D lab's plan rectangle (floor machines)


def inventory() -> list[Item]:
    """Every tray item (kind "item" in the tray plan) and every floor machine, in a fixed order."""
    tp = _load_tray_plan()
    out = []
    for t, v in tp["trays"].items():
        n = 0
        for it in v["items"]:
            if it["kind"] != "item":
                continue
            b = it["box_mm"]
            label, grp, inst = ITEM_INFO.get(it["item"], (it["item"], "misc", True))
            out.append(Item(f"{t}{n}", it["item"], label, grp, inst, b[1] - b[0], b[3] - b[2], b[5] - b[4], tray=t,
                            idx=n, box=tuple(float(x) for x in b)))
            n += 1
    fb = _load_floor_bounds()
    for key, (label, grp, fac) in FLOOR_INFO.items():
        b = fb[key]
        dx, dy = b[1] - b[0], b[3] - b[2]
        w, d = (dx, dy) if fac in ("N", "S") else (dy, dx)
        out.append(Item(key, key, label, grp, True, w, d, b[5] - b[4], facing0=fac,
                        rect0=(b[0], b[2], b[1], b[3])))
    return out


# ============================================================================================ geometry
@dataclass
class Place:
    """Where one item stands in a layout: its footprint's centre (x, y), the way its front faces, and its base height
    (on a bench, a shelf or the floor)."""
    key: str
    x: float
    y: float
    facing: str
    z: float = 0.0
    on: str | None = None          # the bench or shelf it stands on
    zone: str | None = None        # the room or area it stands in

    def rect(self, it: Item) -> tuple:
        w, d = (it.w, it.d) if self.facing in ("N", "S") else (it.d, it.w)
        return (self.x - w / 2, self.y - d / 2, self.x + w / 2, self.y + d / 2)


@dataclass
class Layout:
    name: str
    title: str
    envelope: tuple                                   # (x0, y0, x1, y1), the walls' outer faces
    places: dict = field(default_factory=dict)        # key -> Place
    benches: list = field(default_factory=list)       # dict(rect, h, kind: bench | shelf | table, zone)
    walls: list = field(default_factory=list)         # (x0, y0, x1, y1): wall boxes in plan
    rooms: list = field(default_factory=list)         # dict(name, rect, enclosed)
    aisles: list = field(default_factory=list)        # dict(rect, kind: corridor | aisle | mir)
    docks: list = field(default_factory=list)         # dict(station, x, y, heading)
    chargers: list = field(default_factory=list)      # (x, y, heading)
    arms: list = field(default_factory=list)          # fixed arms: dict(x, y, heading, zone)
    racks: list = field(default_factory=list)         # sample racks at stations: dict(x, y, z)
    notes: list = field(default_factory=list)

    @property
    def area_m2(self) -> float:
        x0, y0, x1, y1 = self.envelope
        return (x1 - x0) * (y1 - y0) / 1e6

    @property
    def area_sqft(self) -> float:
        return self.area_m2 * SQFT_PER_M2


def _round_up(v, m):
    return math.ceil(v / m - 1e-9) * m


@dataclass
class Unit:
    """A thing that stands against a wall in a row: a floor machine, a bench (with its items) or a shelf."""
    kind: str                       # machine | bench | shelf
    w: float                        # along the row
    d: float                        # from the wall
    side: float                     # clearance wanted beside it
    rear: float                     # clearance wanted behind it (to the wall)
    keys: list                      # the items on it (machine: one)
    h: float = 0.0                  # a bench's or shelf's height
    offsets: list = field(default_factory=list)   # bench items' centres along the bench, from its left end


def machine_unit(it: Item) -> Unit:
    return Unit("machine", it.w, it.d, ASSUME["service"], ASSUME["service"], [it.key])


def bench_unit(items: list[Item]) -> Unit:
    """A bench run for these items in this order: 150 mm between them and at the ends, rounded up to whole feet; 30 in
    deep, or 36 in if any is deeper than 712 mm."""
    g = ASSUME["bench_gap"]
    x, offs = g, []
    for it in items:
        offs.append(x + it.w / 2)
        x += it.w + g
    L = _round_up(x, ASSUME["bench_module"])
    pad = (L - x) / 2
    offs = [o + pad for o in offs]
    deep = max(it.d for it in items) > ASSUME["bench_d"] - ASSUME["bench_back"]
    d = ASSUME["bench_d_deep"] if deep else ASSUME["bench_d"]
    return Unit("bench", L, d, 0.0, 0.0, [it.key for it in items], h=ASSUME["bench_h"], offsets=offs)


def shelf_unit(items: list[Item], levels: int) -> Unit:
    """Storage shelving holding these racks one to a level (the tray loads as they are: a rack of jars, a sample store),
    with 40 mm round each."""
    w = max(it.w for it in items) + 80.0
    d = max(it.d for it in items) + 80.0
    offs = [w / 2] * len(items)
    return Unit("shelf", _round_up(w, ASSUME["bench_module"]), d, 0.0, 0.0, [it.key for it in items],
                h=ASSUME["shelf_h"], offsets=offs)


def row_length(units: list[Unit], ends=(0.0, 0.0)) -> float:
    """Units side by side: the gap between two is the larger of their side clearances; at an end, the unit's own
    against the wall's (ends)."""
    if not units:
        return 0.0
    L = max(units[0].side, ends[0])
    for a, b in zip(units[:-1], units[1:]):
        L += a.w + max(a.side, b.side, 0.0 if (a.kind != "machine" and b.kind != "machine") else 0.0)
    L += units[-1].w + max(units[-1].side, ends[1])
    return L


def row_depth(units: list[Unit]) -> float:
    return max((u.rear + u.d for u in units), default=0.0)


def place_row(lay: Layout, inv: dict, units: list[Unit], x0: float, y_wall: float, toward: float, zone: str,
              x_end: float | None = None, door_at: float | None = None):
    """Put a row's units against a wall at y_wall, their fronts facing `toward` (+1: +y, -1: -y), starting at x0. If
    x_end is given, the slack is shared out between the units (so a short row spreads along its wall)."""
    L = row_length(units)
    slack = 0.0 if x_end is None else max(0.0, (x_end - x0) - L)
    n_gaps = len(units) + 1
    extra = slack / n_gaps
    x = x0 + max(units[0].side, 0.0) + extra if units else x0
    facing = "N" if toward > 0 else "S"
    for i, u in enumerate(units):
        if i:
            x += max(units[i - 1].side, u.side) + extra
        y_back = y_wall + toward * u.rear
        yc = y_back + toward * u.d / 2
        if u.kind == "machine":
            lay.places[u.keys[0]] = Place(u.keys[0], x + u.w / 2, yc, facing, zone=zone)
        else:
            rect = (x, min(y_back, y_back + toward * u.d), x + u.w, max(y_back, y_back + toward * u.d))
            lay.benches.append(dict(rect=rect, h=u.h, kind=u.kind, zone=zone, keys=list(u.keys)))
            if u.kind == "bench":
                for k, off in zip(u.keys, u.offsets):
                    it = inv[k]
                    yi = y_back + toward * (ASSUME["bench_back"] + it.d / 2)
                    lay.places[k] = Place(k, x + off, yi, facing, z=u.h, on="bench", zone=zone)
            else:                                     # a shelf: one rack a level, from 150 mm up
                n = len(u.keys)
                for j, k in enumerate(u.keys):
                    z = 150.0 + j * (u.h - 300.0) / max(1, n)
                    lay.places[k] = Place(k, x + u.w / 2, yc, facing, z=z, on="shelf", zone=zone)
        x += u.w


# ============================================================================================ the conventional lab
# Zones along a central corridor (west to east), each with a back row against its far wall and, where it has one, a
# front row against the corridor wall, with a 5 ft aisle between: (name, enclosed, back row, front row). Rows list
# floor machines by key, benches as ("bench", [item keys]) and shelves as ("shelf", [item keys], levels).
def _zones(inv: dict) -> tuple[list, list]:
    by_name = {}
    for it in inv.values():
        by_name.setdefault(it.name, []).append(it.key)

    def k(name, i=0):
        return by_name[name][i]
    north = [
        ("Powder and melt room", True,
         ["glovebox", "repowder", "sieve_cell"],
         [("bench", [k("multi-doser: chain carousel v5 on an HR-202i, 13 powders"),
                     k("Specac Atlas Autotouch 15T, vacuum press"), k("vial rack"),
                     k("SnowX SnowPod", 0), k("SnowX SnowPod", 1)]),
          ("bench", [k("Custom N2 glovebox (purge-only)")]),
          ("shelf", [k("264 powder jars in racks (our design)", 0), k("489 powder jars in racks (our design)", 0),
                     k("489 powder jars in racks (our design)", 1), k("264 powder jars in racks (our design)", 1)], 4)]),
        ("Metal AM bay", True,
         ["eos_m400", "meltio_cell"],
         ["aconity", "ded"]),
        ("Machine shop", True,
         ["wire_edm"],
         [("bench", [k("Makera Carvera"), k("Sentry Air Systems ductless hood, 24 in")])]),
        ("Furnace room", True,
         [("bench", [k("Nabertherm NAT 15/65"), k("water tank with a lift basket, our design")])],
         []),
    ]
    south = [
        ("Mechanical testing", False,
         ["instron_floor", "instron_small",
          ("bench", [k("ZwickRoell zwickiLine Z5.0 TN"), k("Mitutoyo HM-220 Type D (AVPAK)")])],
         [("bench", [k("Plastometrex PLX-Benchtop"), k("KLA iMicro")])]),
        ("SEM room", True,
         [("bench", [k("Hitachi TM4000PlusII"), k("Keyence VHX-7000 (VHX-S750E free-angle stand)")])],
         []),
        ("Analytical and sample prep", False,
         [("bench", [k("Rigaku MiniFlex (6th generation)"), k("Bruker S2 PUMA Series 2, XY Autochanger"),
                     k("Malvern Mastersizer 3000 + Aero S"),
                     k("Powder prep station: XRD holder, SEM stub, XRF cup (our design)")])],
         [("bench", [k("LECO PX500 + disc magazine"), k("LECO MX400"), k("six-shelf disc magazine (ours)")])]),
        ("Wet lab", False,
         ["fumehood", ("bench", [k("Opentrons OT-2"), k("CubXL + NuVant EZstat Pro")])],
         []),
        ("Fabrication", False,
         [("bench", [k("Bambu Lab H2D"), k("Bambu Lab A1 mini"), k("Formlabs Form 4", 0), k("Formlabs Form 4", 1),
                     k("Formlabs Form Wash (2nd Gen)"), k("Formlabs Form Cure (2nd Gen)")])],
         [("bench", [k("DDM Novastar SPR-45VA"), k("Opulo LumenPnP v4.2"), k("Puhui T-962A")])]),
        ("Shipping and storage", False,
         ["packaging", ("shelf", [k("Storage load (our design)", 0), k("Storage load (our design)", 1)], 2)],
         []),
    ]
    return north, south


def _units(spec, inv) -> list[Unit]:
    out = []
    for s in spec:
        if isinstance(s, str):
            out.append(machine_unit(inv[s]))
        elif s[0] == "bench":
            out.append(bench_unit([inv[k] for k in s[1]]))
        else:
            out.append(shelf_unit([inv[k] for k in s[1]], s[2]))
    return out


def conventional(inv: dict | None = None, y_north: float = -1750.0, x_mid: float = 1815.0) -> Layout:
    """The conventional lab: two bands of zones either side of a 6 ft corridor, the north band's north wall at
    y_north (outer face), centred on x_mid."""
    inv = inv or {it.key: it for it in inventory()}
    A_ = ASSUME
    wall, aisle = A_["wall"], A_["aisle"]
    north, south = _zones(inv)
    north = [(n, e, [u for u in b if not isinstance(u, str) or u in inv],
              [u for u in f if not isinstance(u, str) or u in inv]) for n, e, b, f in north]
    north = [z for z in north if z[2] or z[3]]
    bands = []
    for zones in (north, south):
        zs = []
        for name, enclosed, back, front in zones:
            bu, fu = _units(back, inv), _units(front, inv)
            # an entry at the zone's west end: a door in an enclosed zone's wall, a gap in an open zone's front row
            door = A_["door"] + 2 * 150.0 if (enclosed or fu) else 0.0
            wz = max(row_length(bu), row_length(fu) + door, door, A_["module"])
            dz = row_depth(bu) + aisle + row_depth(fu)
            zs.append(dict(name=name, enclosed=enclosed, back=bu, front=fu, w=wz, d=dz, door=door))
        bands.append(zs)
    widths = [sum(z["w"] for z in zs) + wall * (len(zs) - 1) for zs in bands]
    L = max(widths)
    for zs, wsum in zip(bands, widths):                # the shorter band's slack goes to its zones evenly
        extra = (L - wsum) / len(zs)
        for z in zs:
            z["w"] += extra
    dN = max(z["d"] for z in bands[0])
    dS = max(z["d"] for z in bands[1])
    x0 = x_mid - L / 2 - wall
    x1 = x_mid + L / 2 + wall
    yN_in = y_north - wall                            # inner face of the north wall
    yCN = yN_in - dN                                  # the corridor's north edge (the north band's inner wall face)
    yCS = yCN - wall - A_["corridor"]                 # its south edge, at the south band's wall... (wall centred)
    yS_in = yCS - wall - dS
    y0 = yS_in - wall
    lay = Layout("conventional", "Conventional lab", (x0, y0, x1, y_north))
    # outer walls, with the corridor open at both ends (its doors)
    lay.walls += [(x0, y_north - wall, x1, y_north), (x0, y0, x1, y0 + wall),
                  (x0, y0, x0 + wall, yCS), (x0, yCN - wall, x0 + wall, y_north),
                  (x1 - wall, y0, x1, yCS), (x1 - wall, yCN - wall, x1, y_north)]
    lay.aisles.append(dict(rect=(x0 + wall, yCS, x1 - wall, yCN - wall), kind="corridor"))
    for bi, zs in enumerate(bands):
        x = x0 + wall
        north_band = bi == 0
        for zi, z in enumerate(zs):
            zx0, zx1 = x, x + z["w"]
            if north_band:
                zy0, zy1 = yCN, yN_in                     # back wall north, corridor wall south
                back_wall, toward_b = zy1, -1.0
                front_wall, toward_f = zy0, +1.0
            else:
                zy0, zy1 = yS_in, yCS - wall
                back_wall, toward_b = zy0, +1.0
                front_wall, toward_f = zy1, -1.0
            dB = row_depth(z["back"])
            ay = (zy1 - dB - aisle / 2) if north_band else (zy0 + dB + aisle / 2)
            lay.rooms.append(dict(name=z["name"], rect=(zx0, zy0, zx1, zy1), enclosed=z["enclosed"],
                                  entry=(zx0 + 150.0 + A_["door"] / 2, (yCN - wall / 2) if north_band else
                                         (yCS - wall / 2)), aisle_y=ay, band="N" if north_band else "S"))
            place_row(lay, inv, z["back"], zx0, back_wall, toward_b, z["name"], x_end=zx1)
            if z["front"]:
                place_row(lay, inv, z["front"], zx0 + z["door"], front_wall, toward_f, z["name"], x_end=zx1)
            # the aisle inside the zone, in front of its back row
            dB = row_depth(z["back"])
            if north_band:
                lay.aisles.append(dict(rect=(zx0, zy1 - dB - aisle, zx1, zy1 - dB), kind="aisle"))
            else:
                lay.aisles.append(dict(rect=(zx0, zy0 + dB, zx1, zy0 + dB + aisle), kind="aisle"))
            # the wall to the corridor: with a door if enclosed, open otherwise; and the wall to the next zone
            if north_band:
                cw = (zx0, yCN - wall, zx1, yCN)
            else:
                cw = (zx0, yCS - wall, zx1, yCS)
            if z["enclosed"]:
                dx0 = zx0 + 150.0
                lay.walls += [(zx0, cw[1], dx0, cw[3]), (dx0 + A_["door"], cw[1], zx1, cw[3])]
            if zi < len(zs) - 1:
                lay.walls.append((zx1, zy0 if north_band else zy0, zx1 + wall, zy1 if north_band else yCS))
            x = zx1 + wall
    lay.notes.append("Zones along a 6 ft corridor; each zone's back row against its far wall, its front row against "
                     "the corridor wall, a 5 ft aisle between them.")
    return lay


# ============================================================================================ the flat automated lab
FLAT_UNITS = 4          # MiR250 + UR12e mobile manipulators: stations are spread over the whole floor (our choice)


def flat(conv: Layout, inv: dict) -> Layout:
    """The conventional plan, automated: nothing moves and the walls stay. A docking target in front of every floor
    machine and every bench, a fixed arm with a sample rack on a pedestal beside each bench whose row has room for one
    (600 mm free at the bench's end), two chargers at the corridor's east end, FLAT_UNITS mobile manipulators."""
    lay = Layout("flat", "Automated, same floor plan", conv.envelope, dict(conv.places), list(conv.benches),
                 list(conv.walls), list(conv.rooms), list(conv.aisles))
    leads = _bench_leads(conv)
    for k, p in conv.places.items():
        it = inv[k]
        if p.on == "shelf" or not it.instrument or (p.on == "bench" and k not in leads):
            continue
        sgn = 1.0 if p.facing == "N" else -1.0
        r = p.rect(it)
        y_front = r[3] if sgn > 0 else r[1]
        if p.on == "bench":
            b = next(b for b in conv.benches if k in b["keys"])
            y_front = b["rect"][3] if sgn > 0 else b["rect"][1]
        lay.docks.append(dict(station=k, x=p.x, y=y_front + sgn * (450.0 + 290.0), heading=0.0))
    # what stands in each row, to find room beside a bench
    rects = [b["rect"] for b in conv.benches] + [p.rect(inv[k]) for k, p in conv.places.items() if p.on is None]
    zones = {r["name"]: r["rect"] for r in conv.rooms}
    for b in conv.benches:
        if b["kind"] != "bench":
            continue
        x0, y0, x1, y1 = b["rect"]
        zx0, _, zx1, _ = zones[b["zone"]]
        right = min([r[0] for r in rects if r[0] >= x1 - 1 and r[1] < y1 and r[3] > y0 and r is not b["rect"]] +
                    [zx1])
        left = max([r[2] for r in rects if r[2] <= x0 + 1 and r[1] < y1 and r[3] > y0 and r is not b["rect"]] +
                   [zx0 + 150.0 + ASSUME["door"] + 150.0])
        if right - x1 >= 600.0:
            lay.arms.append(dict(x=x1 + 40.0 + 260.0, y=(y0 + y1) / 2, side=1, toward=(-1.0, 0.0), zone=b["zone"]))
        elif x0 - left >= 600.0:
            lay.arms.append(dict(x=x0 - 40.0 - 260.0, y=(y0 + y1) / 2, side=-1, toward=(1.0, 0.0), zone=b["zone"]))
        else:
            continue
        lay.racks.append(dict(x=lay.arms[-1]["x"], y=(y0 + y1) / 2, z=880.0, zone=b["zone"]))
    # two chargers against the east wall of the last room on the south side, in its aisle, facing west
    x0, y0, x1, y1 = conv.envelope
    last = max((r for r in conv.rooms if r.get("band") == "S"), key=lambda r: r["rect"][2])
    for dy in (-400.0, 400.0):
        lay.chargers.append((x1 - ASSUME["wall"] - 487.0 - 10.0, last["aisle_y"] + dy, 90.0))
    lay.notes.append(f"{FLAT_UNITS} mobile manipulators; {len(lay.docks)} docking targets; {len(lay.arms)} fixed arms, "
                     f"each with a sample rack; {len(lay.chargers)} chargers. A docked MiR250 (580 mm wide) leaves "
                     "0.94 m of a 5 ft aisle: less than the 1.45 m one needs to drive by, so robots wait in the aisles.")
    return lay


def _bench_leads(lay: Layout) -> set:
    """The first instrument on each bench: one dock a bench."""
    return {b["keys"][0] for b in lay.benches if b["kind"] == "bench" and b["keys"]}


# ============================================================================================ the vertical lab
VLM_KEYS = ("vlm1", "vlm2")
VLM = dict(w=2830.0, d=3124.0, x=(0.0, 3630.0), y=0.0)       # the 3-D lab's Shuttles (out/tray_plan.json floor)


def vertical(inv: dict) -> Layout:
    """The two Shuttles where the 3-D lab has them (x 0 and 3630, fronts at y -1562), every benchtop item on its tray,
    the floor machines in a north row (with the Shuttles) and a south row either side of the 3.0 m MiR aisle, packed
    by the same rules as the conventional lab (0.6 m service clearance beside and behind each machine), and the two
    scale-up machines (no MiR dock) at the aisle's east end."""
    A_ = ASSUME
    wall, svc = A_["wall"], A_["service"]
    y_front_n = -1562.0
    y_aisle_n = y_front_n - A_["dock_zone"]
    y_aisle_s = y_aisle_n - A_["mir_aisle"]
    y_front_s = y_aisle_s - A_["dock_zone"]
    # north row: west of the Shuttles, then east of them, each packed from the Shuttles outward
    west = ["sieve_cell", "repowder", "glovebox"]
    east = ["aconity"]
    lay = Layout("vertical", "Vertical lab", (0, 0, 0, 0))
    x = -VLM["w"] / 2
    for k in west:
        it = inv[k]
        w = it.w if k != "glovebox" else it.d       # the glovebox turned as in the 3-D lab: its long side along y
        dd = it.d if k != "glovebox" else it.w
        x -= svc + w
        lay.places[k] = Place(k, x + w / 2, y_front_n + dd / 2, "S" if k != "glovebox" else "S")
    xw = x - svc
    x = VLM["x"][1] + VLM["w"] / 2
    for k in east:
        it = inv[k]
        x += svc
        lay.places[k] = Place(k, x + it.w / 2, y_front_n + it.d / 2, "S")
        x += it.w
    xe_n = x + svc
    # south row, west to east: the two Instrons, the chargers, the fume hood, the DED, the wire EDM, packaging
    south = ["instron_floor", "instron_small", "CHG", "CHG", "CHG", "fumehood", "ded", "wire_edm", "packaging"]
    x = xw + svc
    chg_w, chg_d = 622.0, 487.0
    first = True
    for k in south:
        if k == "CHG":
            if not first:
                x += 600.0
            lay.chargers.append((x + chg_w / 2, y_front_s - chg_d / 2, 90.0))
            x += chg_w
            first = False
            continue
        it = inv[k]
        if not first:
            x += svc
        lay.places[k] = Place(k, x + it.w / 2, y_front_s - it.d / 2, "N")
        x += it.w
        first = False
    xe_s = x + svc
    # the scale-up machines at the aisle's east end, facing west into it, their long sides along y
    xe = max(xe_n, xe_s)
    yc = (y_aisle_n + y_aisle_s) / 2
    x_cap = xe + svc
    if "eos_m400" in inv and "meltio_cell" in inv:
        eos, mel = inv["eos_m400"], inv["meltio_cell"]
        cap_w = max(eos.d, mel.d)
        lay.places["meltio_cell"] = Place("meltio_cell", x_cap + mel.d / 2, yc + svc / 2 + mel.w / 2, "W")
        lay.places["eos_m400"] = Place("eos_m400", x_cap + eos.d / 2, yc - svc / 2 - eos.w / 2, "W")
        x1 = x_cap + cap_w + svc
    else:                                            # (the sensitivity without them: no cap)
        x1 = xe
        x_cap = xe + svc
    # the envelope: the deepest row's back + clearance, both ends
    y_n = max(VLM["d"] / 2 + svc, max(p.rect(inv[k])[3] + svc for k, p in lay.places.items() if p.facing == "S"))
    y_s = min(p.rect(inv[k])[1] - svc for k, p in lay.places.items() if p.facing == "N")
    ys_caps = [lay.places[k].rect(inv[k]) for k in ("meltio_cell", "eos_m400") if k in lay.places]
    if ys_caps:
        y_n = max(y_n, max(r[3] for r in ys_caps) + svc)
        y_s = min(y_s, min(r[1] for r in ys_caps) - svc)
    lay.envelope = (xw - wall, y_s - wall, x1 + wall, y_n + wall)
    ex0, ey0, ex1, ey1 = lay.envelope
    lay.walls += [(ex0, ey1 - wall, ex1, ey1), (ex0, ey0, ex1, ey0 + wall), (ex0, ey0, ex0 + wall, ey1),
                  (ex1 - wall, ey0, ex1, ey1)]
    lay.aisles.append(dict(rect=(ex0 + wall, y_aisle_s, x_cap - svc, y_aisle_n), kind="mir"))
    lay.aisles.append(dict(rect=(ex0 + wall, y_aisle_n, x_cap - svc, y_front_n), kind="dock"))
    lay.aisles.append(dict(rect=(ex0 + wall, y_front_s, x_cap - svc, y_aisle_s), kind="dock"))
    lay.rooms.append(dict(name="Vertical lab", rect=(ex0 + wall, ey0 + wall, ex1 - wall, ey1 - wall), enclosed=True))
    # every benchtop item on its tray (the tray plan), so no place on the floor
    for k, it in inv.items():
        if it.tray is not None:
            lay.places[k] = Place(k, float("nan"), float("nan"), "S", on=f"tray {it.tray}")
    for i, xs in enumerate(VLM["x"]):
        lay.places[VLM_KEYS[i]] = Place(VLM_KEYS[i], xs, VLM["y"], "S")
    # docks: every north- and south-row station a MiR serves, on the aisle's dock lines
    for k, p in lay.places.items():
        if p.on is not None or k in ("eos_m400", "meltio_cell") or math.isnan(p.x):
            continue
        y = y_front_n - 370.0 if p.facing == "S" else y_front_s + 370.0
        lay.docks.append(dict(station=k, x=p.x, y=y, heading=0.0))
    lay.notes.append("North row: glovebox, atomizer, sieving cell, two Shuttles, LPBF. South row: two Instrons, three "
                     "chargers, fume hood, DED, wire EDM, packaging. East end: EOS M 400-4 and Meltio cell (no MiR "
                     "dock).")
    return lay


# ============================================================================================ areas and counts
def counts(inv: dict) -> dict:
    inst = [it for it in inv.values() if it.instrument]
    bench = [it for it in inst if it.tray is not None]
    floor = [it for it in inst if it.tray is None]
    return dict(instruments=len(inst), benchtop=len(bench), floor=len(floor),
                benchtop_labels=[it.label for it in bench], floor_labels=[it.label for it in floor])


def check(lay: Layout, inv: dict) -> list[str]:
    """Overlaps between footprints on the floor (benches, shelves, floor machines, walls), and anything outside the
    envelope. -> a list of problems (empty: none)."""
    rects = []
    for k, p in lay.places.items():
        if k in VLM_KEYS:
            rects.append((k, (p.x - VLM["w"] / 2, p.y - VLM["d"] / 2, p.x + VLM["w"] / 2, p.y + VLM["d"] / 2)))
            continue
        if p.on is not None or math.isnan(p.x):
            continue
        rects.append((k, p.rect(inv[k])))
    for i, b in enumerate(lay.benches):
        rects.append((f"{b['kind']}{i}", b["rect"]))
    probs = []
    ex0, ey0, ex1, ey1 = lay.envelope
    for n, r in rects:
        if r[0] < ex0 - 1 or r[1] < ey0 - 1 or r[2] > ex1 + 1 or r[3] > ey1 + 1:
            probs.append(f"{lay.name}: {n} outside the envelope")
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            a, b = rects[i][1], rects[j][1]
            if a[0] < b[2] - 1 and b[0] < a[2] - 1 and a[1] < b[3] - 1 and b[1] < a[3] - 1:
                probs.append(f"{lay.name}: {rects[i][0]} overlaps {rects[j][0]}")
        for w in lay.walls:
            a = rects[i][1]
            if a[0] < w[2] - 1 and w[0] < a[2] - 1 and a[1] < w[3] - 1 and w[1] < a[3] - 1:
                probs.append(f"{lay.name}: {rects[i][0]} in a wall")
    return probs


CATS = ("floor machines", "benches, shelves and Shuttles", "service clearance", "aisles and corridor", "walls",
        "other floor")


def breakdown(lay: Layout, inv: dict, res: float = 25.0) -> dict:
    """Where a layout's floor goes, m2 by category, rasterized at res mm: walls; floor machines (and chargers);
    benches, shelves and the Shuttles; service clearance (0.6 m beside and behind each floor machine, where nothing
    else is); aisles, the corridor and the MiR aisle's dock lanes; the rest."""
    x0, y0, x1, y1 = lay.envelope
    nx, ny = int(math.ceil((x1 - x0) / res)), int(math.ceil((y1 - y0) / res))
    grid = np.full((ny, nx), 5, np.int8)                      # other floor

    def fill(r, cat, only=None):
        i0, i1 = int((r[0] - x0) / res), int(math.ceil((r[2] - x0) / res))
        j0, j1 = int((r[1] - y0) / res), int(math.ceil((r[3] - y0) / res))
        i0, j0 = max(i0, 0), max(j0, 0)
        sub = grid[j0:j1, i0:i1]
        if only is None:
            sub[...] = cat
        else:
            sub[np.isin(sub, only)] = cat
    for a in lay.aisles:
        fill(a["rect"], 3)
    svc = ASSUME["service"]
    for k, p in lay.places.items():
        if p.on is not None or math.isnan(p.x) or k in VLM_KEYS:
            continue
        r = p.rect(inv[k])
        fill((r[0] - svc, r[1] - svc, r[2] + svc, r[3] + svc), 2, only=[5, 3])
    for k, p in lay.places.items():
        if k in VLM_KEYS:
            fill((p.x - VLM["w"] / 2, p.y - VLM["d"] / 2, p.x + VLM["w"] / 2, p.y + VLM["d"] / 2), 1)
        elif p.on is None and not math.isnan(p.x):
            fill(p.rect(inv[k]), 0)
    for b in lay.benches:
        fill(b["rect"], 1)
    for c in lay.chargers:
        fill((c[0] - 311, c[1] - 244, c[0] + 311, c[1] + 244), 0)
    for w in lay.walls:
        fill(w, 4)
    cell = res * res / 1e6
    out = {CATS[i]: round(float((grid == i).sum() * cell), 1) for i in range(len(CATS))}
    return out


def summary(layouts: list[Layout], inv: dict) -> dict:
    c = counts(inv)
    rows = []
    for lay in layouts:
        x0, y0, x1, y1 = lay.envelope
        rows.append(dict(name=lay.name, title=lay.title, length_m=round((x1 - x0) / 1000, 2),
                         width_m=round((y1 - y0) / 1000, 2), area_m2=round(lay.area_m2, 1),
                         area_sqft=round(lay.area_sqft), instruments=c["instruments"],
                         per_1000_sqft=round(c["instruments"] / lay.area_sqft * 1000, 1),
                         sqft_per_instrument=round(lay.area_sqft / c["instruments"]),
                         docks=len(lay.docks), arms=len(lay.arms), chargers=len(lay.chargers),
                         breakdown_m2=breakdown(lay, inv), notes=lay.notes))
    return dict(rows=rows, counts=c, assume=ASSUME, ecl=ECL)


# Emerald Cloud Lab, as published (notes/twin_floorspace.md has the sources and what each figure covers)
ECL = dict(
    ssf=dict(sqft=15000, m2=1400, instruments="more than 100 items of equipment",
             source="The Guardian, Tom Ireland, 2022-09-11, 'Cloud labs and remote research aren't the future of "
                    "science - they're here' (reprinted by CMU: cmu.edu/ambassadors/december-2022/pdf/"
                    "guardian_cloud-labs.pdf)"),
    austin=dict(sqft=105000, instruments="over 230 unique types of instruments",
                source="Emerald Cloud Lab press release, 2023-02-28 (PR Newswire, 'Emerald Cloud Lab to relocate "
                       "state-of-the-art facility from South San Francisco to Austin')"),
    cmu=dict(sqft=16000, m2=1500, source="The Guardian, 2022-09-11 (as above): Carnegie Mellon's cloud lab, "
                                         "built and run with Emerald"),
)


def build_all(exclude=()) -> tuple[dict, list[Layout]]:
    inv = {it.key: it for it in inventory() if it.key not in exclude}
    conv = conventional(inv)
    fl = flat(conv, inv)
    ver = vertical(inv)
    return inv, [conv, fl, ver]


def to_json(lay: Layout) -> dict:
    return dict(name=lay.name, title=lay.title, envelope=[round(v, 1) for v in lay.envelope],
                area_m2=round(lay.area_m2, 2), area_sqft=round(lay.area_sqft, 1),
                places={k: dict(x=round(p.x, 1) if not math.isnan(p.x) else None,
                                y=round(p.y, 1) if not math.isnan(p.y) else None, facing=p.facing,
                                z=round(p.z, 1), on=p.on) for k, p in lay.places.items()},
                benches=[dict(b, rect=[round(v, 1) for v in b["rect"]]) for b in lay.benches],
                walls=[[round(v, 1) for v in w] for w in lay.walls],
                rooms=[dict(r, rect=[round(v, 1) for v in r["rect"]]) for r in lay.rooms],
                aisles=[dict(a, rect=[round(v, 1) for v in a["rect"]]) for a in lay.aisles],
                docks=lay.docks, chargers=lay.chargers, arms=lay.arms, racks=lay.racks, notes=lay.notes)


def main():
    inv, lays = build_all()
    OUTD.mkdir(parents=True, exist_ok=True)
    s = summary(lays, inv)
    probs = [p for lay in lays for p in check(lay, inv)]
    js = dict(note="written by twin/video/floorspace.py: three layouts of the 3-D lab's equipment (design layouts, "
                   "not built labs)", summary=s, problems=probs,
              inventory=[dict(key=it.key, name=it.name, label=it.label, group=it.group, instrument=it.instrument,
                              w=round(it.w), d=round(it.d), h=round(it.h), tray=it.tray) for it in inv.values()],
              layouts={lay.name: to_json(lay) for lay in lays})
    # the sensitivity: the same, without the two scale-up printers (EOS M 400-4, Meltio cell)
    inv2, lays2 = build_all(exclude=("eos_m400", "meltio_cell"))
    js["without_scaleup"] = dict(note="the same rules and zones without the EOS M 400-4 and the Meltio cell",
                                 summary=summary(lays2, inv2), problems=[p for lay in lays2 for p in check(lay, inv2)])
    (OUTD / "layouts.json").write_text(json.dumps(js, indent=1) + "\n")
    for r in s["rows"]:
        print(f"{r['title']:<28} {r['length_m']:6.2f} x {r['width_m']:5.2f} m = {r['area_m2']:6.1f} m2 = "
              f"{r['area_sqft']:6,} sq ft; {r['per_1000_sqft']:.1f} instruments / 1000 sq ft")
    print(s["counts"]["instruments"], "instruments:", s["counts"]["benchtop"], "benchtop,", s["counts"]["floor"],
          "floor")
    print("problems:", probs or "none")
    for r in js["without_scaleup"]["summary"]["rows"]:
        print(f"  without the scale-up printers: {r['title']:<28} {r['length_m']:6.2f} x {r['width_m']:5.2f} m = "
              f"{r['area_m2']:6.1f} m2 = {r['area_sqft']:6,} sq ft; {r['per_1000_sqft']:.1f} / 1000 sq ft")


if __name__ == "__main__":
    main()

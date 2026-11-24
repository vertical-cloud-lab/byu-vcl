"""Where everything stands in the facility, in the pilot cell's own frame (mm; x east, y north, the floor at z = 0).

The pilot cell is PR #318's lab exactly as ``setup_lab.build`` lays it out (Shuttle 1 at the origin, its opening to the
south, the east-west aisle in front of it). The rest copies that lab's way of working: every station stands in a row
along an aisle, its front to the aisle, and a MiR250 docks alongside it on the row's dock line (warehouse.py: the
fronts 370 mm north of the north row's dock line and 2,338 mm from the aisle's centre line, the 3.0 m aisle two
MiR250s pass in). The halls (all ours):

* **VLM hall**, the pilot cell's aisle carried on east: 16 Shuttles a side, 35 ft tall, 3,630 mm apart as the
  pilot cell's two are (800 mm between claddings, room for a MiR250 to turn).
* **Atomization hall**, behind the VLM hall's north row: two aisles, rePowders with a sieving cell beside each, as in
  the pilot cell.
* **Print hall**, east of it on the same two aisles: Aconity MIDIs, and EOS M 400-4s at the far end.
* **Test and fabrication hall**, north: an aisle of Instron 68FM-100 frames with their furnaces and wire EDMs facing
  them, then the DED machines (InssTek MX-Lab), Meltio repair cells, fume hoods, packaging stations and gloveboxes,
  all copies of the pilot cell's own.
* **Gas atomization hall**, north of the pilot cell: four VIGA-class plants (``gas_atomizer.py``), with the bulk argon
  and nitrogen tanks outside its west wall.
"""
from __future__ import annotations

AISLE_HALF = 2338.0          # an aisle's centre line to the fronts of the stations on either side (warehouse.py)
DOCK_OFF = 1968.0            # its centre line to a dock line
SHUTTLE_FRONT = 1562.0       # a Shuttle's centre to its front face (vlm: UNIT_D / 2 + SKIN)
SHUTTLE_PITCH = 3630.0       # vlm.SHUTTLE_X[2]
YC_VLM = -3900.0             # the pilot cell's aisle (warehouse.AISLE: -2400 .. -5400)

BUILDING = dict(x0=-17000.0, x1=104000.0, y0=-14000.0, y1=41000.0, wall_h=4500.0, wall_t=300.0)

# the atomization and print halls' two aisles: rows of rePowders 2,460 mm deep, back to back with 600 mm between
YC_AT = (7860.0, 18056.0)
YC_TEST = 33000.0

VLM_X = [18500.0 + i * SHUTTLE_PITCH for i in range(16)]
RP_X = [20000.0 + i * 4600.0 for i in range(8)]          # rePowders; each with its sieving cell 2,197 mm east of it
SIEVE_DX = 2197.0
MIDI_X = [60000.0 + i * 3000.0 for i in range(10)]
EOS_X = [93500.0, 99000.0]
TEST_X = [23000.0 + i * 3400.0 for i in range(10)]
NORTH_N = [("ded", 60000.0 + i * 3000.0) for i in range(6)] + [("meltio_cell", 83500.0), ("meltio_cell", 92500.0)]
NORTH_S = [("fumehood", 60000.0 + i * 2200.0) for i in range(4)] + [("packaging", 71500.0), ("packaging", 76000.0),
                                                                    ("glovebox", 82500.0), ("glovebox", 86000.0)]
DEPTH = {"ded": 777.0, "meltio_cell": 3430.0, "fumehood": 959.0, "packaging": 753.0, "glovebox": 2305.0}
GAS_AT = [(-6500.0, 16500.0), (8500.0, 16500.0), (-6500.0, 31500.0), (8500.0, 31500.0)]
TANKS = [(-21500.0, 12000.0, "argon"), (-21500.0, 17500.0, "argon"), (-21500.0, 23000.0, "nitrogen")]


def face(yc: float, side: str) -> float:
    """y of the fronts of a row on `side` ("N": the row north of the aisle, facing south) of the aisle at yc."""
    return yc + AISLE_HALF if side == "N" else yc - AISLE_HALF


def dock_y(yc: float, side: str) -> float:
    return yc + DOCK_OFF if side == "N" else yc - DOCK_OFF


def heading(side: str) -> float:
    """The MiR250's heading on a dock line: its arm side (its +y) towards the stations."""
    return 0.0 if side == "N" else 180.0


def stations() -> list[dict]:
    """Every placed station: dict(kind, x, y, turn, side, yc, dock_x, hall, id). (x, y) is the middle of its
    footprint for a machine (its asset's frame), the centre of the unit for a Shuttle; turn 0 faces south."""
    out = []
    sid = 0

    def add(kind, x, side, yc, depth, hall, dock_x=None):
        nonlocal sid
        yf = face(yc, side)
        y = yf + depth / 2 if side == "N" else yf - depth / 2
        out.append(dict(kind=kind, x=x, y=y, turn=0.0 if side == "N" else 180.0, side=side, yc=yc,
                        dock_x=x if dock_x is None else dock_x, hall=hall, id=sid))
        sid += 1

    for x in VLM_X:
        add("shuttle", x, "N", YC_VLM, 2 * SHUTTLE_FRONT, "vlm")
        add("shuttle", x, "S", YC_VLM, 2 * SHUTTLE_FRONT, "vlm")
    for yc in YC_AT:
        for side in ("S", "N"):
            for x in RP_X:
                add("repowder", x, side, yc, 2460.0, "atomize")
                add("sieve_cell", x + SIEVE_DX, side, yc, 630.0, "atomize")
            for x in MIDI_X:
                add("aconity", x, side, yc, 1234.0, "print")
    for yc, side in ((YC_AT[0], "N"), (YC_AT[1], "S")):
        for x in EOS_X:
            add("eos_m400", x, side, yc, 1743.0, "print")
    for x in TEST_X:
        add("instron_floor", x, "N", YC_TEST, 1053.0, "test")
        add("wire_edm", x, "S", YC_TEST, 2544.0, "test")
    for kind, x in NORTH_N:
        add(kind, x, "N", YC_TEST, DEPTH[kind], "fab")
    for kind, x in NORTH_S:
        add(kind, x, "S", YC_TEST, DEPTH[kind], "fab")
    return out


def fleets() -> list[dict]:
    """The MiR250 + UR12e units outside the pilot cell: each keeps to one dock line and a stretch of it, so no two
    meet. dict(hall, yc, side, x0, x1, kinds)."""
    f = []
    for side in ("N", "S"):
        for a, b in ((VLM_X[0], VLM_X[4]), (VLM_X[5], VLM_X[10]), (VLM_X[11], VLM_X[15])):
            f.append(dict(hall="vlm", yc=YC_VLM, side=side, x0=a, x1=b, kinds=("shuttle",)))
    for yc in YC_AT:
        for side in ("N", "S"):
            f.append(dict(hall="atomize", yc=yc, side=side, x0=RP_X[0], x1=RP_X[3] + SIEVE_DX,
                          kinds=("repowder", "sieve_cell")))
            f.append(dict(hall="atomize", yc=yc, side=side, x0=RP_X[4], x1=RP_X[7] + SIEVE_DX,
                          kinds=("repowder", "sieve_cell")))
            f.append(dict(hall="print", yc=yc, side=side, x0=MIDI_X[0], x1=MIDI_X[4], kinds=("aconity",)))
            f.append(dict(hall="print", yc=yc, side=side, x0=MIDI_X[5], x1=EOS_X[-1], kinds=("aconity", "eos_m400")))
    for side in ("N", "S"):
        f.append(dict(hall="test", yc=YC_TEST, side=side, x0=TEST_X[0], x1=TEST_X[-1],
                      kinds=("instron_floor", "wire_edm")))
    f.append(dict(hall="fab", yc=YC_TEST, side="N", x0=NORTH_N[0][1], x1=NORTH_N[-1][1], kinds=("ded", "meltio_cell")))
    f.append(dict(hall="fab", yc=YC_TEST, side="S", x0=NORTH_S[0][1], x1=NORTH_S[-1][1],
                  kinds=("fumehood", "packaging", "glovebox")))
    return f


# what the pilot cell (PR #318's lab) has of each, on top of the halls
PILOT = {"shuttle": 2, "repowder": 1, "sieve_cell": 1, "aconity": 1, "eos_m400": 1, "meltio_cell": 1, "ded": 1,
         "instron_floor": 1, "instron_small": 1, "wire_edm": 1, "fumehood": 1, "packaging": 1, "glovebox": 1, "units": 2}


def counts(pilot: bool = True) -> dict:
    """How many of each the facility has (the pilot cell's included unless pilot=False)."""
    c: dict[str, int] = {}
    for s in stations():
        c[s["kind"]] = c.get(s["kind"], 0) + 1
    c["gas_atomizer"] = len(GAS_AT)
    c["units"] = len(fleets())
    if pilot:
        for k, v in PILOT.items():
            c[k] = c.get(k, 0) + v
    return c

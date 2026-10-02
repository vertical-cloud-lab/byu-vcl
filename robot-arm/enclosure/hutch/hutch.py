"""Geometry of the raised deck (hutch) at spot D (#229), shared by the FE model, the CAD and the renders.

Coordinates are the dome model's: x along the wall, y from the room (-y) to the wall (+y), z up
from the table top, metres. Boards are listed in the hutch's own frame (centred on the deck);
`YC` moves the whole hutch back against the wall.
"""

from dataclasses import dataclass

import numpy as np

IN = 0.0254
T = 0.703 * IN            # 3/4 in plywood, actual thickness (same as the dome model's panel)
W = 48 * IN               # the deck is the whole 4 x 4 ft sheet, 1219 mm square
CLEAR = 0.500             # table top to the underside of the deck
TABLE = dict(x=1.290, y=1.360, h=0.76)   # spot D, two 680 x 1290 mm tables; the height is assumed
WALL_Y = TABLE["y"] / 2   # the back edge of the tables is against room 158's wall
GAP = 0.005               # deck to wall
YC = WALL_Y - GAP - W / 2  # hutch centre, 65 mm behind the middle of the tables

# The spine: a closed plywood box under the arm, running side panel to side panel.
SPINE_Y = 0.125           # web mid-planes at y = +/-125 mm (the arm's M5 square is +/-35 mm)
SPINE_H = 0.100           # web depth below the deck
PAD_X = 0.300             # doubler glued under the deck, inside the box, where the arm sits
BASE_PATCH = 0.100        # the arm's foot, taken as rigid over a 100 mm square

# Plywood, effective values for 3/4 in hardwood-faced veneer-core panel (see README "Assumptions").
E_PAR, E_PERP = 7.0e9, 4.0e9       # Pa, along and across the face grain
G_INPLANE, G_TRANSVERSE = 0.45e9, 0.10e9
NU = 0.07
RHO = 600.0                        # kg/m^3, about 10.7 kg per m^2 of 3/4 in panel

# Every option stands on the same deck and two full-depth side panels, glued and screwed.
OPTIONS = {
    "plain": dict(label="Plain hutch", note="deck on two side panels", back=False, spine=False, wall=False),
    "ribs": dict(label="1. Ribs", note="+ spine box under the arm", back=False, spine=True, wall=False),
    "panels": dict(label="2. Shear panels", note="+ back panel", back=True, spine=False, wall=False),
    "ribs+panels": dict(label="3. Ribs + shear panels", note="+ spine box + back panel", back=True, spine=True,
                        wall=False),
    "ribs+wall": dict(label="4. Ribs + wall anchor", note="+ spine box, deck screwed to a wall ledger",
                      back=False, spine=True, wall=True),
}
RECOMMENDED = "ribs+panels"


@dataclass
class Board:
    name: str
    lo: tuple            # min corner, hutch frame (m)
    hi: tuple            # max corner
    grain: int           # axis the face grain runs along (0 x, 1 y, 2 z)
    cut: tuple           # (length along the grain, width) as cut from the sheet, m
    color: str = "#e3d2ad"
    step: int = 0        # build step it goes in at
    tags: tuple = ()

    @property
    def size(self):
        return np.subtract(self.hi, self.lo)

    @property
    def centre(self):
        return (np.add(self.lo, self.hi)) / 2


def boards(opt):
    """The plywood parts of one option, in the hutch frame."""
    o = OPTIONS[opt] if isinstance(opt, str) else opt
    h, xi = W / 2, W / 2 - T              # half deck, inner face of a side panel
    out = []
    for s, nm in ((-1, "left"), (1, "right")):
        lo, hi = sorted((s * xi, s * h))
        out.append(Board(f"side-{nm}", (lo, -h, 0), (hi, h, CLEAR), 1, (W, CLEAR), step=1, tags=("side",)))
    if o["back"]:
        out.append(Board("back", (-xi, h - T, 0), (xi, h, CLEAR), 0, (2 * xi, CLEAR), step=2, tags=("back",)))
    if o["spine"]:
        zb = CLEAR - SPINE_H
        for s, nm in ((-1, "front"), (1, "rear")):
            y0 = s * SPINE_Y - T / 2
            out.append(Board(f"spine-web-{nm}", (-xi, y0, zb), (xi, y0 + T, CLEAR), 0, (2 * xi, SPINE_H), step=3,
                             tags=("spine",)))
        out.append(Board("spine-bottom", (-xi, -SPINE_Y - T / 2, zb - T), (xi, SPINE_Y + T / 2, zb), 0,
                         (2 * xi, 2 * SPINE_Y + T), step=4, tags=("spine",)))
        py = SPINE_Y - T / 2
        out.append(Board("spine-pad", (-PAD_X / 2, -py, CLEAR - T), (PAD_X / 2, py, CLEAR), 0, (PAD_X, 2 * py),
                         step=3, tags=("spine", "pad")))
    out.append(Board("deck", (-h, -h, CLEAR), (h, h, CLEAR + T), 0, (W, W), step=5, tags=("deck",)))
    return out


def deck_top():
    return CLEAR + T


# The arm's four M5 holes: 70 mm square on the deck centre (PiPER manual).
HOLE_SQ = 0.070


def hole_xy():
    a = HOLE_SQ / 2
    return [(sx * a, sy * a) for sx in (-1, 1) for sy in (-1, 1)]

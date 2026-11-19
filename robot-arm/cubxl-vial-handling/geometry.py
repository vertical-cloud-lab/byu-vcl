"""Geometry for #266: Chris's CubXL mock-up parts, the real CubXL+ deck, and the proposed handoff dock.

Everything is in metres in the arm's frame unless a name says _mm: J1's axis is the origin, on the bench
top, +y points from the arm towards the CubXL and +z is up. The CubXL stands side-on to the arm, so that
its gantry X axis (the long, 334 mm tool window) runs along world +y, radial from J1.

Nothing vendored lives here. The mock-up parts come from the zip attached to #266 and the real deck from
Ursa's Cubware repo, both fetched into CACHE on first use.
"""

import io
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
CACHE = Path("/tmp/cubxl-vial-handling")
MOCKUP_ZIP = "https://github.com/user-attachments/files/33156849/CubXL.mock.up.parts.zip"  # #266, 7 Oct 2026
CUBWARE = "https://raw.githubusercontent.com/Ursa-Laboratories/Cubware/352aa95/cubxl_plus"
PANDA_DECK = CUBWARE + "/deck/polycarbonate_deck/PandaDeck.stl"
MOCKUP_FILES = {"deck": "CubXL mock up.3mf", "holder": "9VialHolder.3mf", "key": "9VialHolder-key.3mf",
                "vial": "Vial.3mf"}


def _fetch(url, name):
    path = CACHE / name
    if not path.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(url, timeout=120) as r:
            path.write_bytes(r.read())
    return path


def mockup_parts():
    """Chris's four parts as meshes in mm, exactly as exported from Onshape (units: metres)."""
    zf = zipfile.ZipFile(_fetch(MOCKUP_ZIP, "mockup.zip"))
    out = {}
    for key, name in MOCKUP_FILES.items():
        scene = trimesh.load(io.BytesIO(zf.read(name)), file_type="3mf", force="scene")
        m = list(scene.dump())[0]
        m.apply_scale(1000.0)
        out[key] = m
    return out


def panda_deck():
    """Cubware's PandaDeck, the CubXL+ deck plate (mm)."""
    return trimesh.load(_fetch(PANDA_DECK, "PandaDeck.stl"), force="mesh")


def slot_grid(deck):
    """Plate size, slot size and slot pitch from a mid-thickness section of a deck plate (mm)."""
    top = deck.bounds[1][2]
    def area(z):
        sec = deck.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        return 0.0 if sec is None else sum(p.area for p in sec.to_2D()[0].polygons_full)

    a0 = area(top - 0.5)
    t = next(d for d in np.arange(1.0, 60.0, 0.5) if area(top - d) < 0.5 * a0) - 0.5   # plate, not the legs
    p2, T = deck.section(plane_origin=[0, 0, top - t / 2], plane_normal=[0, 0, 1]).to_2D()
    holes = []
    for poly in p2.polygons_full:
        for h in poly.interiors:
            c = trimesh.transform_points(np.c_[np.asarray(h.coords), np.zeros(len(h.coords))], T)
            holes.append((*c[:, :2].min(0), *c[:, :2].max(0)))
    h = np.array(holes)
    w, d = h[:, 2] - h[:, 0], h[:, 3] - h[:, 1]
    slot = (w > 8) & (d > 8) & (np.maximum(w, d) > 20)
    cx, cy = (h[slot, 0] + h[slot, 2]) / 2, (h[slot, 1] + h[slot, 3]) / 2
    ux, uy = np.unique(np.round(cx, 1)), np.unique(np.round(cy, 1))
    long_x = np.median(w[slot]) > np.median(d[slot])
    return dict(plate_mm=np.round(deck.extents[:2], 1).tolist(),
                thickness_mm=round(float(t), 1),
                slots=int(slot.sum()), grid=[len(ux), len(uy)],
                slot_mm=[round(float(np.median(w[slot])), 2), round(float(np.median(d[slot])), 2)],
                pitch_mm=[round(float(np.median(np.diff(ux))), 2), round(float(np.median(np.diff(uy))), 2)],
                slot_long_axis="x" if long_x else "y")


# ------------------------------------------------------------------ the CubXL, as built (from the repo configs)
# cubos/configs/gantry/cub_xl_ben_pipette_capper.yaml, 2026-09-26 calibration
WORKING_VOLUME_MM = dict(x=(0.0, 388.0), y=(0.0, 233.665), z=(0.0, 121.0))
PIPETTE_OFFSET_MM = (54.0, 12.999)   # capper is the reference tool, offset (0, 0)
VIAL_PITCH_MM = 33.0                  # 9-vial holder (and every committed deck file)


def tool_window(axis):
    """Deck span that BOTH the capper and the pipette can reach (CubOS: gantry = deck - offset)."""
    lo, hi = WORKING_VOLUME_MM[axis]
    off = PIPETTE_OFFSET_MM["xy".index(axis)]
    return max(lo, lo + off), min(hi, hi + off)


def vials_that_fit(axis, pitch=VIAL_PITCH_MM):
    lo, hi = tool_window(axis)
    return int(np.floor((hi - lo) / pitch)) + 1


# ------------------------------------------------------------------ PROVER XL 4030 envelope (approximate)
# SainSmart's published overall size is 641 x 755.5 x 580 mm (X x Y x Z) with a 400 x 300 x 110 mm working area.
# The rail, beam and backboard positions below are scaled from the issue #133 photos and are PLACEHOLDERS:
# measure them on the real machine before trusting any clearance in the figures.
FRAME = dict(x=0.641, y=0.7555, h=0.580)
DECK_TOP = 0.0586        # Chris's mock-up: 48.6 mm legs + 10 mm plate. Measure the real deck.
RAIL = dict(w=0.060, h=0.110)          # Y-axis rail + side plate, each side (placeholder)
END = dict(w=0.040, h=0.090)           # front and back members (placeholder)
BEAM = dict(w=0.080, z0=0.300, z1=0.380)  # gantry bridge (placeholder)
BOARD = dict(w=0.300, h=0.270, z0=0.180)  # black instrument backboard on the Z carriage (placeholder)
TOOLS_LOW = 0.150        # lowest tool point with Z at the top of travel (placeholder)

# Placement: J1 at the origin, CubXL side frame 0.20 m away, the dock's carrier axis on the arm's centre line.
# The gantry's travel is assumed centred on the deck, and the carrier axis sits at gantry Y = 45 mm.
FRAME_NEAR_Y = 0.20
DECK = dict(x=0.490, y=0.480)  # PandaDeck, along gantry Y (world x) and gantry X (world y)
GANTRY_Y0_X = -0.045           # world x of gantry Y = 0 (the CubXL's front, operator side, is towards -x)
GANTRY_X0_Y = FRAME_NEAR_Y + (FRAME["x"] - DECK["y"]) / 2 + (DECK["y"] - 0.391) / 2  # world y of gantry X = 0
DECK_FRONT_X = GANTRY_Y0_X - (DECK["x"] - 0.2367) / 2
FRAME_FRONT_X = DECK_FRONT_X - (FRAME["y"] - DECK["x"]) / 2


def window_world():
    """Common capper + pipette window as world (x0, x1), (y0, y1)."""
    (gx0, gx1), (gy0, gy1) = tool_window("x"), tool_window("y")
    return (GANTRY_Y0_X + gy0 / 1000, GANTRY_Y0_X + gy1 / 1000), (GANTRY_X0_Y + gx0 / 1000, GANTRY_X0_Y + gx1 / 1000)


def frame_boxes():
    """(name, bounds) boxes for the CubXL envelope, world metres."""
    x0, x1 = FRAME_FRONT_X, FRAME_FRONT_X + FRAME["y"]
    y0, y1 = FRAME_NEAR_Y, FRAME_NEAR_Y + FRAME["x"]
    tools_x = GANTRY_Y0_X + WORKING_VOLUME_MM["y"][1] / 1000          # gantry parked at Y max ...
    park_x = tools_x + 0.035                                           # ... beam behind the backboard
    board_y1 = y1 - RAIL["w"] - 0.02                                   # ... and the carriage at the far X end
    return [
        ("near rail", ((x0, x1), (y0, y0 + RAIL["w"]), (0, RAIL["h"]))),
        ("far rail", ((x0, x1), (y1 - RAIL["w"], y1), (0, RAIL["h"]))),
        ("front member", ((x0, x0 + END["w"]), (y0, y1), (0, END["h"]))),
        ("back member", ((x1 - END["w"], x1), (y0, y1), (0, END["h"]))),
        ("gantry beam, parked", ((park_x, park_x + BEAM["w"]), (y0, y1), (BEAM["z0"], BEAM["z1"]))),
        ("backboard, parked", ((park_x - 0.012, park_x), (board_y1 - BOARD["w"], board_y1),
                               (BOARD["z0"], BOARD["z0"] + BOARD["h"]))),
        ("tools, parked", ((tools_x - 0.03, park_x - 0.012), (board_y1 - 0.20, board_y1 - 0.06),
                           (TOOLS_LOW, BOARD["z0"]))),
    ]


def deck_origin():
    """World position of the PandaDeck's (0, 0) corner, deck plate centred in the frame."""
    cx = FRAME_FRONT_X + FRAME["y"] / 2
    cy = FRAME_NEAR_Y + FRAME["x"] / 2
    return np.array([cx - DECK["x"] / 2, cy - DECK["y"] / 2, DECK_TOP - 0.010])


# ------------------------------------------------------------------ the proposed dock and carrier
DOCK = dict(base_t=0.008, len=0.330, wid=0.110, lead_in=0.003, wall_h=0.012)
CARRIER = dict(len=0.2974, wid=0.0334, h=0.035, seat=0.018, near_y=0.370)
VIAL = dict(body_d=0.027, cap_d=0.028, body_h=0.0457, h=0.0642)
POST = dict(d=0.027, groove_z=0.050, groove_depth=0.002, groove_h=0.006)  # z from the carrier's underside
SINGLE_POCKETS = [(0.052, 0.405), (0.052, 0.450)]  # (x, y) of two loose single-vial transfer pockets


def carrier_z0():
    return DECK_TOP + DOCK["base_t"]


def slot_y(i):
    """World y of carrier slot i = 1..9 (slot 5 carries the handle post)."""
    return CARRIER["near_y"] + CARRIER["wid"] / 2 + (i - 1) * VIAL_PITCH_MM / 1000


def grasp_point():
    """Pad centre on the handle post's groove."""
    return np.array([0.0, slot_y(5), carrier_z0() + POST["groove_z"]])


def vial_grasp_height():
    """Middle of the vial body left exposed between the holder top and the cap."""
    z_lo = carrier_z0() + CARRIER["h"]
    z_hi = carrier_z0() + CARRIER["seat"] + VIAL["body_h"]
    return (z_lo + z_hi) / 2, z_hi - z_lo

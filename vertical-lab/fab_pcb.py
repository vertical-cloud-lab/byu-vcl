"""PCB assembly for the vertical cloud lab: a semi-automatic stencil printer and an open-source pick-and-place (#303).

Both are ``instruments.Instrument``s, rendered by ``fab_tour.py`` and laid out on tray H by ``fab_trays.py``. Frame as in
``instruments.py``: x to the right and y away from you when you face the front, z up from the tray, origin at the centre
of the footprint, millimetres. The envelopes are the makers' figures; the layout in between is read off their photos and
is approximate, as ``SPECS`` in ``instruments.py`` says for the others.
"""
from __future__ import annotations

from instruments import Instrument, Joint, _piece, _xcyl, _ycyl, box, cyl, rbox  # noqa: F401

MATERIALS = {
    "lumen_black": (0.10, 0.10, 0.11, 1.0, 0.25),     # LumenPnP's black printed parts and anodised extrusion
    "lumen_yellow": (0.96, 0.70, 0.12, 1.0, 0.30),    # its yellow corner pieces
    "staging": (0.07, 0.07, 0.08, 1.0, 0.45),         # the black staging-plate PCBs
    "gold": (0.85, 0.66, 0.25, 1.0, 0.85),            # their gold pads and the feeders' contacts
    "chip": (0.06, 0.06, 0.07, 1.0, 0.35),            # a moulded IC package
    "paste": (0.66, 0.67, 0.69, 1.0, 0.35),           # solder paste
    "fr4": (0.08, 0.42, 0.20, 1.0, 0.45),             # a bare green board
    "ddm_grey": (0.83, 0.84, 0.83, 1.0, 0.25),        # the stencil printer's light grey cabinet
    "ddm_blue": (0.12, 0.30, 0.60, 1.0, 0.35),
    "squeegee": (0.82, 0.83, 0.85, 1.0, 0.90),        # a stainless squeegee blade
}


# ===================================================================================================== LumenPnP
# Opulo LumenPnP v4, an open-source desktop pick-and-place (github.com/opulo-inc/lumenpnp, DESIGN_DECISIONS.md and
# bom.json at main, 2026-10-14; Opulo's v4 hero photo): V-slot 20 x 20 extrusion (seven 600 mm lengths in the BOM) on
# four printed legs; an X gantry riding on two Y gantries; a head with two nozzles on NEMA 11 hollow-shaft steppers,
# a down-looking top camera and an up-looking bottom camera, each with a ring light; staging plates that are 120 x
# 600 mm PCBs with a hole array, three across; powered feeders on the front and back rails; boards up to 225 x 400 mm.
# Opulo publishes no overall size: W and D are the 600 mm extrusions plus the legs, H is scaled from the photo (about
# +-15 %). Black parts with yellow corner pieces, as in the photo.
LUMEN = dict(W=680.0, D=680.0, H=450.0, leg=44.0, rail_z=275.0, plate_z=228.0, gy0=-215.0, gtravel=430.0,
             hx0=-240.0, htravel=480.0, tip_z=268.0, drop=26.0)


def lumenpnp() -> Instrument:
    p = LUMEN
    W, D, H = p["W"], p["D"], p["H"]
    inst = Instrument("lumenpnp", "Pick-and-place, open source", "Opulo LumenPnP v4", (W, D, H),
                      "Opulo's LumenPnP repository (DESIGN_DECISIONS.md, bom.json: 600 mm V-slot, two nozzles, top and "
                      "bottom vision, 120 x 600 mm staging plates, boards to 225 x 400 mm) and its v4 photo; overall "
                      "size estimated from the extrusions and the photo")
    inst.notes = ["Opulo publishes no overall size; 680 x 680 x 450 mm is the 600 mm extrusions plus the legs, and the "
                  "height scaled from Opulo's photo (about +-15 %).",
                  "Open hardware: the CAD is FreeCAD and the firmware is Marlin, driven by OpenPnP.",
                  "It needs no compressed air: its vacuum pumps are on board."]
    rz, pz = p["rail_z"], p["plate_z"]
    xl = W / 2 - p["leg"] / 2                        # the legs' and the Y rails' centre lines
    yl = D / 2 - p["leg"] / 2
    body = _piece(inst, "body")
    for sx in (-1, 1):
        for sy in (-1, 1):
            leg = box(sx * xl - 22, sy * yl - 22, 0, sx * xl + 22, sy * yl + 22, rz)
            leg = leg.cut(box(sx * xl - 30, sy * yl - 8, 30, sx * xl + 30, sy * yl + 8, 110))     # the leg's cutout
            body.add(f"leg {sx} {sy}", leg, "lumen_black")
            body.add(f"corner {sx} {sy}", box(sx * xl - 24, sy * yl - 24, rz - 30, sx * xl + 24, sy * yl + 24, rz),
                     "lumen_yellow")
        body.add(f"y rail {sx}", box(sx * xl - 10, -yl, rz, sx * xl + 10, yl, rz + 20), "lumen_black")
        body.add(f"y guide {sx}", box(sx * xl - 6, -yl + 30, rz + 20, sx * xl + 6, yl - 30, rz + 28), "steel")
        body.add(f"side rail {sx}", box(sx * xl - 10, -yl, pz - 20, sx * xl + 10, yl, pz), "lumen_black")
    for sy in (-1, 1):
        body.add(f"x rail {sy}", box(-xl, sy * yl - 10, pz - 20, xl, sy * yl + 10, pz), "lumen_black")
    body.add("lower front rail", box(-xl, -yl - 10, 120, xl, -yl + 10, 140), "lumen_black")
    body.add("staging plates", box(-xl + 12, -yl + 12, pz, xl - 12, yl - 12, pz + 1.6), "staging")
    for i in range(-5, 6):                           # a few rows of the plates' gold pads, for the look
        for j in range(-5, 6):
            if abs(j) < 2 and i < -2:
                continue
            body.add(f"pad {i} {j}", cyl(8, 0.4, x=50.0 * j, y=50.0 * i + 10, z=pz + 1.6), "gold")
    cam_y = -yl + 120
    body.add("bottom camera ring", cyl(46, 4, y=cam_y, z=pz + 1.6).cut(cyl(30, 6, y=cam_y, z=pz)), "lumen_yellow")
    body.add("bottom camera lens", cyl(30, 1, y=cam_y, z=pz + 1.0), "window")
    body.add("bottom camera", box(-30, cam_y - 30, pz - 120, 30, cam_y + 30, pz - 2), "lumen_black")
    body.add("datum mounts", box(-130, 0, pz + 1.6, -118, 120, pz + 10).union(box(-130, -12, pz + 1.6, 90, 0, pz + 10)),
             "lumen_yellow")
    body.add("feeder strip", box(-xl + 60, -yl - 14, 128, xl - 60, -yl - 10, 165), "staging")
    for i in range(25):                               # the 25 numbered feeder slots on the lower front rail
        x = -xl + 75 + i * (2 * xl - 150) / 24
        body.add(f"feeder slot {i}", box(x - 5, -yl - 15, 150, x + 5, -yl - 14, 162), "gold")
        body.add(f"back tab {i}", box(x - 4, yl - 22, pz + 1.6, x + 4, yl - 8, pz + 14), "lumen_yellow")
    for i, x in enumerate((-180.0, -150.0, -120.0)):  # three powered feeders on the front, reels behind the rail
        body.add(f"feeder {i}", box(x - 6, -yl - 40, 140, x + 6, -yl + 70, pz + 12), "lumen_black")
        body.add(f"feeder tape {i}", box(x - 4, -yl + 30, pz + 12, x + 4, -yl + 60, pz + 12.6), "inst_light")
        body.add(f"reel {i}", _xcyl(130, 8, x=x - 4, y=-yl - 70, z=140), "polycarb")
    body.add("control box", box(-xl + 40, yl - 160, 30, -xl + 200, yl - 40, 140), "lumen_black")
    body.add("y motor", box(-xl - 21, yl - 50, rz + 20, -xl + 21, yl - 8, rz + 62), "inst_dark")
    gy = p["gy0"]
    gantry = _piece(inst, "gantry")
    gantry.add("x gantry", box(-xl - 10, gy - 10, rz + 28, xl + 10, gy + 10, rz + 48), "lumen_black")
    gantry.add("x guide", box(-xl + 30, gy - 14, rz + 32, xl - 30, gy - 10, rz + 44), "steel")
    for sx in (-1, 1):
        gantry.add(f"y carriage {sx}", box(sx * xl - 24, gy - 40, rz + 24, sx * xl + 24, gy + 40, rz + 52),
                   "lumen_yellow" if sx > 0 else "lumen_black")
    gantry.add("x motor", box(-xl - 30, gy - 20, rz + 52, -xl + 12, gy + 22, rz + 94), "inst_dark")
    gantry.add("drag chain", box(-xl + 40, gy + 12, rz + 48, xl - 60, gy + 34, rz + 66), "lumen_black")
    hx = p["hx0"]
    head = _piece(inst, "head")
    hy = gy - 40
    tz = p["tip_z"]                                  # the nozzles' tips, 28 mm over the board
    head.add("head plate", box(hx - 45, hy - 6, tz + 22, hx + 45, hy + 26, H - 30), "lumen_black")
    for sx in (-1, 1):
        head.add(f"z stepper {sx}", box(hx + sx * 22 - 14, hy - 34, tz + 72, hx + sx * 22 + 14, hy - 6, H - 30),
                 "inst_dark")
        head.add(f"air line {sx}", cyl(4, 30, x=hx + sx * 22, y=hy - 20, z=H - 30), "inst_blue" if sx < 0 else "inst_red")
    head.add("top camera", box(hx - 12, hy - 40, tz + 16, hx + 12, hy - 6, tz + 62), "inst_black")
    head.add("top ring light", cyl(30, 6, x=hx, y=hy - 23, z=tz + 10), "inst_white")
    nozzle = _piece(inst, "nozzle")
    for sx in (-1, 1):
        nozzle.add(f"nozzle shaft {sx}", cyl(8, 56, x=hx + sx * 22, y=hy - 20, z=tz + 16), "chrome")
        nozzle.add(f"nozzle tip {sx}", cyl(3, 16, x=hx + sx * 22, y=hy - 20, z=tz), "brass")
    tip = (hx - 22, hy - 20, tz)                      # nozzle 1's tip, modelled
    part = _piece(inst, "part")
    part.add("part on the nozzle", box(tip[0] - 5, tip[1] - 5, tip[2] - 2, tip[0] + 5, tip[1] + 5, tip[2]), "chip")
    board = _piece(inst, "load")
    bx, by, bz = -20.0, 60.0, pz + 10                # the board on its datum mounts
    board.add("board", box(bx - 110, by - 60, bz, bx + 110, by + 60, bz + 1.6), "fr4")
    for i in range(10):
        board.add(f"pad row {i}", box(bx - 90 + 20 * i, by - 40, bz + 1.6, bx - 84 + 20 * i, by + 40, bz + 1.7), "paste")
    chips = {"chip1": (bx - 50, by + 10), "chip2": (bx + 10, by - 15), "chip3": (bx + 60, by + 20)}
    for name, (cx, cy) in chips.items():
        _piece(inst, name).add(name, box(cx - 9, cy - 9, bz + 1.7, cx + 9, cy + 9, bz + 4.0), "chip")
    # where the head goes, as joint values: gantry v (y = gy0 + v * travel of nozzle 1), head v (x)
    def at(x, y):
        return (round((x - tip[0]) / p["htravel"], 4), round((y - tip[1]) / p["gtravel"], 4))
    feed = at(-150.0, -yl + 45)
    camv = at(0.0, cam_y)
    place = {k: at(*xy) for k, xy in chips.items()}
    inst.joints = {
        "gantry": Joint("slide", vec=(0, p["gtravel"], 0), v0=0.5),
        "head": Joint("slide", vec=(p["htravel"], 0, 0), parent="gantry", v0=0.5),
        "nozzle": Joint("slide", vec=(0, 0, -p["drop"]), parent="head"),
        "part": Joint("fade", parent="nozzle"),
        "load": Joint("path", path=((0, -700, 380), (0, -200, 300), (0, 0, 120), (0, 0, 0))),
        **{k: Joint("fade", parent="load") for k in chips},
    }

    def go(hv, gv):
        return {"head": (None, hv), "gantry": (None, gv)}
    acts = [("A bare board, pasted on tray H's stencil printer, goes onto the staging plate against the datum "
             "mounts.", 2.0, {"load": (0.0, 1.0), **go(1.0, 1.0)})]
    for i, k in enumerate(chips):
        first = i == 0
        acts += [
            ("The head goes to a feeder; nozzle 1 drops and picks a part by vacuum." if first else "", 1.2 if first
             else 0.8, go(*feed)),
            ("", 0.5, {"nozzle": (0.0, 1.0), "part": (0.0, 1.0)}),
            ("", 0.4, {"nozzle": (1.0, 0.0)}),
            ("Over the up-looking camera, which measures the part's offset and rotation on the nozzle." if first
             else "", 1.2 if first else 0.7, go(*camv)),
            ("To its place on the board, found by the top camera from the board's fiducials; down, and the vacuum "
             "lets go." if first else "", 1.3 if first else 0.8, go(*place[k])),
            ("", 0.5, {"nozzle": (0.0, 1.0), "part": (1.0, 0.0), k: (0.0, 1.0)}),
            ("", 0.4, {"nozzle": (1.0, 0.0)}),
        ]
    acts += [("Three parts placed; the board goes on to reflow.", 2.0, {**go(1.0, 1.0), "load": (1.0, 0.0)})]
    inst.actions = acts
    inst.labels = [("two nozzles, top camera", (hx, hy - 30, rz + 60), (0.16, 0.20)),
                   ("powered feeders", (-150, -yl - 20, 200), (0.14, 0.78)),
                   ("up-looking camera", (0, cam_y, pz), (0.80, 0.80))]
    inst.cam = (0.9, -1.6, 1.05)
    return inst


# ===================================================================================================== stencil printer
# DDM Novastar SPR-45VA, a benchtop semi-automatic stencil printer with vision assist: 762 W x 889 D x 406 H mm (30 x
# 35 x 16 in, Pentalogix's listing; "H x W x D 16 x 30 x 35 in"), about 73 kg (160 lb, the SPR-45's listed weight);
# frame holder for stencil frames up to 584 x 584 mm (23 x 23 in); dual squeegees on a motorised print head and an
# automatic power frame lift (DDM Novastar's SPR-45 description at its resellers). The layout is generic for the type
# and read from resellers' photos: a low grey cabinet with the controls at the front, the board nest on the deck, the
# frame holder over it on two lift columns, the print head riding across the frame on side rails. 889 mm deep is more
# than the tray's 840, so on the tray it stands turned 90 degrees.
STENCIL = dict(W=762.0, D=889.0, H=406.0, deck=230.0, frame=584.0, lift=110.0, stroke=420.0)


def stencil_printer() -> Instrument:
    p = STENCIL
    W, D, H = p["W"], p["D"], p["H"]
    inst = Instrument("stencil", "Solder paste stencil printer, semi-automatic", "DDM Novastar SPR-45VA", (W, D, H),
                      "Pentalogix's SPR-45VA listing (762 x 889 x 406 mm, 584 mm frames); DDM Novastar's SPR-45 "
                      "description (160 lb, dual squeegees, power frame lift); layout from resellers' photos")
    inst.notes = ["The layout between the published outline is generic for a benchtop semi-automatic printer.",
                  "Semi-automatic: someone, or the arm, puts the board on the nest and takes it off; the machine "
                  "aligns, prints and separates.",
                  "889 mm deep against the tray's 840, so it goes on the tray turned 90 degrees.",
                  "Solder paste lives in a fridge and needs time to warm up; the paste on the stencil dries out over "
                  "a few hours, so someone has to wipe the stencil."]
    dz = p["deck"]
    fr = p["frame"]
    zs = dz + 70.0                                    # underside of the stencil when it is down on the board
    body = _piece(inst, "body")
    body.add("cabinet", rbox(W, D - 60, dz, 14, y=30), "ddm_grey")
    body.add("front panel", _wedge_front(W, dz), "ddm_grey")
    body.add("control panel", box(W / 2 - 260, -D / 2 - 4, 60, W / 2 - 40, -D / 2, 160), "inst_dark")
    body.add("screen", box(W / 2 - 245, -D / 2 - 6, 90, W / 2 - 140, -D / 2 - 4, 150), "screen_on")
    body.add("start buttons", box(-W / 2 + 40, -D / 2 - 3, 100, -W / 2 + 160, -D / 2, 130), "inst_green")
    body.add("e-stop", _ycyl(34, 14, x=-W / 2 + 210, y=-D / 2 - 14, z=115), "inst_red")
    body.add("logo", box(-80, -D / 2 - 2, 40, 80, -D / 2, 55), "ddm_blue")
    body.add("deck", box(-W / 2 + 10, -D / 2 + 40, dz, W / 2 - 10, D / 2 - 10, dz + 8), "inst_dark")
    body.add("board nest", box(-150, -110, dz + 8, 150, 110, zs - 1.6), "aluminium")
    # the frame holder slides on two lift posts, which pass through it and stop inside the published height; a sleeve
    # under the holder keeps hold of each post with the frame up
    px = W / 2 - 45
    for sx in (-1, 1):
        body.add(f"lift column {sx}", box(sx * px - 25, -60, dz + 8, sx * px + 25, 60, H - 4), "inst_dark")
    body.add("vision camera", box(-40, D / 2 - 90, dz + 8, 40, D / 2 - 30, zs - 20), "inst_black")
    frame = _piece(inst, "frame")
    ring = box(-W / 2 + 20, -fr / 2 - 30, zs + 20, W / 2 - 20, fr / 2 + 30, zs + 40).cut(
        box(-fr / 2, -fr / 2, zs + 19, fr / 2, fr / 2, zs + 41))
    for sx in (-1, 1):
        ring = ring.cut(box(sx * px - 27, -62, zs + 19, sx * px + 27, 62, zs + 41))
        frame.add(f"lift sleeve {sx}", box(sx * px - 30, -65, zs - 50, sx * px + 30, 65, zs + 20).cut(
            box(sx * px - 27, -62, zs - 51, sx * px + 27, 62, zs + 21)), "inst_dark")
    frame.add("frame holder", ring, "inst_black")
    frame.add("stencil frame", box(-fr / 2, -fr / 2, zs, fr / 2, fr / 2, zs + 38).cut(
        box(-fr / 2 + 32, -fr / 2 + 32, zs - 1, fr / 2 - 32, fr / 2 - 32, zs + 39)), "aluminium")
    frame.add("stencil foil", box(-fr / 2 + 32, -fr / 2 + 32, zs, fr / 2 - 32, fr / 2 - 32, zs + 0.8), "stainless")
    for i in range(10):                               # the apertures, where the board's pad rows are
        frame.add(f"aperture {i}", box(-90 + 20 * i, -40, zs + 0.8, -84 + 20 * i, 40, zs + 0.9), "inst_dark")
    for sx in (-1, 1):
        frame.add(f"head rail {sx}", box(sx * (fr / 2 + 6) - 8, -fr / 2 - 20, zs + 40, sx * (fr / 2 + 6) + 8,
                                         fr / 2 + 20, zs + 52), "steel")
    head = _piece(inst, "squeegee")
    y0 = -p["stroke"] / 2
    head.add("print head", box(-fr / 2 - 10, y0 - 40, zs + 52, fr / 2 + 10, y0 + 40, H - 4), "ddm_blue")
    head.add("head motor", box(-60, y0 - 20, H - 4, 60, y0 + 20, H), "inst_dark")
    for sy in (-1, 1):
        blade = box(-150, -1.5, zs + 1, 150, 1.5, zs + 52).rotate((0, 0, zs + 52), (1, 0, zs + 52), sy * 30)
        head.add(f"squeegee {sy}", blade.translate((0, y0 + sy * 18, 0)), "squeegee")
    head.add("paste bead", _xcyl(10, 280, x=-140, y=y0 + 40, z=zs + 6), "paste")
    board = _piece(inst, "load")
    board.add("board", box(-110, -60, zs - 1.6, 110, 60, zs), "fr4")
    paste = _piece(inst, "paste")
    for i in range(10):
        paste.add(f"paste row {i}", box(-90 + 20 * i, -40, zs, -84 + 20 * i, 40, zs + 0.6), "paste")
    inst.joints = {
        "frame": Joint("slide", vec=(0, 0, p["lift"]), v0=1.0),
        "squeegee": Joint("slide", vec=(0, p["stroke"], 0), parent="frame"),
        "load": Joint("path", path=((0, -650, 60), (0, -300, 40), (0, 0, 20), (0, 0, 0))),
        "paste": Joint("fade", parent="load"),
    }
    inst.actions = [
        ("The frame is up. A bare board goes onto the vacuum nest.", 2.0, {"load": (0.0, 1.0)}),
        ("The vision assist lines the stencil's apertures up with the pads; the frame comes down onto the board.", 1.6,
         {"frame": (1.0, 0.0)}),
        ("The print head drives a squeegee across: paste rolls ahead of the blade and fills the apertures.", 2.0,
         {"squeegee": (0.0, 1.0)}),
        ("The frame lifts straight up off the board, leaving the paste on the pads.", 1.4,
         {"frame": (0.0, 1.0), "paste": (0.0, 1.0)}),
        ("The pasted board goes on to the pick-and-place.", 1.8, {"load": (1.0, 0.0), "squeegee": (1.0, 0.0)}),
    ]
    inst.labels = [("stencil in its frame", (fr / 2 - 40, -fr / 2 + 40, zs + p["lift"] + 30), (0.84, 0.28)),
                   ("print head, dual squeegees", (-fr / 2, y0, H), (0.15, 0.22)),
                   ("controls", (W / 2 - 150, -D / 2, 140), (0.82, 0.78))]
    inst.cam = (0.8, -1.6, 1.2)
    return inst


def _wedge_front(W, dz):
    """The cabinet's sloped front, from 60 mm deep at the floor to the deck edge."""
    import cadquery as cq
    D = STENCIL["D"]
    pts = [(-D / 2 + 60, 0), (-D / 2, 0), (-D / 2, dz - 60), (-D / 2 + 60, dz)]
    return cq.Workplane("YZ").polyline(pts).close().extrude(W - 28).translate((-W / 2 + 14, 0, 0))


REGISTRY = {"stencil": stencil_printer, "lumenpnp": lumenpnp}

"""Plan B (PR 274, Ben, 2026-10-22): the CubXL as a charge-filling station for the aluminium-alloy workflow.

PR 176's doser, close to its built size, hangs from the CubXL's head in place of the capper and pipette, turned so that
its auger runs along X and it tilts about Y. Its powders are auger cartridges (PR 176's tube with its flight, v4
outlet, moulded 44T gear and cap) stored level, along X, in a vertical stack at the back of the deck. The drive clips
onto one cartridge at a time from the front: the tube snaps into two C-clips cut from PR 176's split-clamp brackets and
the gear meets the NEMA 11's 20T pinion. It then fills the lab's Al charge cups (PR 277's shop drawing: 3/4" 6063 bar,
2.750" long, 1/2" bore 2.25" deep), 50 of them in a rack on the deck.

A concept sketch, not a design. Kept from PR 176's STEP: the tube, gear and cap, both brackets (cut open on the side
facing the stack), the NEMA 11, its leads and its pinion. Left out: the base, the hinged mounting plate, both tilt
servos' cradles, the tap collar and solenoid, and the PCB. New, as placeholder boxes: a spine over the brackets and the
stepper, a hinge above the cartridge, one tilt servo, the head bracket, the stack and the cup rack. The CubXL is
cubxl_shuttle.py's stand-in (only the deck is real CAD), with the capper and pipette taken off.

Needs what ../miniature-doser/cubxl_shuttle.py needs (its docstring has the commands), then:
    POWDER_DOSER=/tmp/powder-doser/cad/text-to-cad PANDA_DECK=/tmp/PandaDeck.step \
        xvfb-run -a -s "-screen 0 1920x1080x24" python alloy_cubxl.py          # --fit prints the numbers only
Writes alloy_cubxl_views.png and alloy_cubxl.gif next to this file.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pyvista as pv
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "miniature-doser"))
import cubxl_shuttle as C                               # noqa: E402
from cubxl_shuttle import ALU, BLACK, BLUE, STEEL, box, cyl, framed, render  # noqa: E402
from module_views import INK, MUTED, D, font            # noqa: E402

# --- the charge cups (PR 277's atomizer-charge/drawing: as made) and their rack -----------------------------------
IN = 25.4
CUP_OD, CUP_H, CUP_BORE, CUP_DEPTH = 0.75 * IN, 2.75 * IN, 0.5 * IN, 2.25 * IN
CUP_PITCH, CUP_COLS, CUP_ROWS = 30.0, 10, 5             # 50 cups, 10 along X by 5 along Y
CUP_X0, CUP_Y0 = 152.0, 112.0                           # the first cup's centre (machine frame, as cubxl_shuttle)
RACK_T = 12.0                                           # printed rack plate; the cups stand on the deck through it
RIM = CUP_H                                             # rims above the deck
RIM_GAP = 4.0                                           # the outlet face's lowest point over the rim while filling
AL6063 = (0.78, 0.79, 0.82)

# --- the drive, in PR 176's doser frame (doser_cad): auger along +y, outlet at y = 35.4, axis at z = 38.25 -------
HINGE_D = np.array([0.0, 100.0, 80.0])                  # new hinge, above the cartridge: about the doser's x (machine Y)
AXIS_DROP = HINGE_D[2] - D.AUGER_AXIS[2]                # 41.75: the auger's axis below the hinge, level
CLIP_OPEN = 13.0                                        # the brackets are cut away beyond this x: open towards the stack
SPINE = ((-58.0, -25.0), (78.0, 182.0), (62.0, 70.0))   # over the brackets' front halves and the stepper, clear of
                                                        #   the stack's gears (|x| < 23)
HINGE_BLOCK = ((-64.0, -50.0), (90.0, 110.0), (68.0, 92.0))
FORK = ((-70.0, -64.0), (82.0, 118.0), (70.0, 170.0))  # fixed: holds the pin, hangs from the head bracket, which
CROSS = 170.0                                           #   crosses over the cartridge at this doser z: over the stack
SERVO = ((-108.0, -70.0), (80.0, 120.0), (70.0, 90.0))  # MG996R-size, spline on the hinge axis, outside the fork
DOSE, LEVEL = 35.0, 0.0                                  # deg, cap end up / level for moves and pick-up

# --- the stack: level cartridges along X, one above another, at the back of the reach ------------------------------
LEVELS = (38.0, 83.0, 128.0)                            # axis heights; 45 mm pitch: the brackets reach 29 mm below the
                                                        #   axis and 24 above, the gear 23 either way
STACK_Y = 330.0                                         # the cartridges' axis (machine y): 4.7 mm inside the Y reach
STACK_OUTLET_X = 286.0                                  # the stored cartridges' outlet faces (machine x)
ENGAGE = 36.0                                           # the head comes in from this far in front, then clips on
POWDERS = (("4047", (0.70, 0.72, 0.76)), ("Si", (0.42, 0.44, 0.52)), ("AlSi10Mg", (0.62, 0.66, 0.60)))
TRAVEL_AXIS = 112.0                                     # the axis while carrying over the rims (brackets clear by 13)


def to_machine(p, deg, hinge_m):
    """Doser-frame points -> machine: tilt `deg` about the doser's x through HINGE_D (positive lifts the cap end),
    turn +90 deg about z (auger along machine -x from the outlet, stepper in front), put HINGE_D at hinge_m."""
    q = np.asarray(p, float) - HINGE_D
    c, s = np.cos(np.radians(deg)), np.sin(np.radians(deg))
    y, z = q[:, 1] * c - q[:, 2] * s, q[:, 1] * s + q[:, 2] * c
    return np.column_stack([-y, q[:, 0], z]) + hinge_m


def _xform(m, deg, hinge_m):
    m = m.copy()
    m.points = to_machine(m.points, deg, hinge_m)
    return m.compute_normals(split_vertices=True, feature_angle=35.0)


def _leaves():
    L = D._leaf_cache()
    pick = lambda *names: D._poly(*_merge([L[k] for k in L if k.split("/")[-1] in names]))
    return dict(tube=pick("auger"), cap=pick("auger_cap"), brackets=pick("bracket_front", "bracket_rear"),
                stepper=pick("stepper_motor"), leads=pick("stepper_leads"), pinion=pick("stepper_pinion"))


def _merge(ms):
    off, P, F = 0, [], []
    for p, t in ms:
        P.append(p)
        F.append(t + off)
        off += len(p)
    return np.vstack(P), np.vstack(F)


_L = None


def leaves():
    global _L
    if _L is None:
        _L = _leaves()
        _L["brackets"] = _L["brackets"].clip_box((CLIP_OPEN, 1e3, -1e3, 1e3, -1e3, 1e3), invert=True)
        _L["brackets"] = _L["brackets"].extract_surface(algorithm=None).triangulate()
    return _L


def dbox(b):
    return pv.Box((b[0][0], b[0][1], b[1][0], b[1][1], b[2][0], b[2][1])).triangulate()


MAT = D.MATERIALS
PRINTED = (0.93, 0.93, 0.90)                            # PR 176's printed parts, as on the bench (PLA/PETG)


def cartridge(deg, hinge_m, powder=0):
    """The tube (with flight and gear) and its cap, colour-coded cap by powder."""
    lv = leaves()
    return [(_xform(lv["tube"], deg, hinge_m), PRINTED, 0.2), (_xform(lv["cap"], deg, hinge_m), POWDERS[powder][1], 0.3)]


def drive(deg, hinge_m):
    """What hangs on the head: the moving frame (brackets, stepper, pinion, spine, hinge block) at `deg` and the fixed
    fork, servo and bracket up to the head."""
    lv = leaves()
    moving = [(_xform(lv["brackets"], deg, hinge_m), PRINTED, 0.2),
              (_xform(lv["stepper"], deg, hinge_m), MAT["vac_motor"][0], 0.3),
              (_xform(lv["leads"], deg, hinge_m), (0.75, 0.2, 0.2), 0.2),
              (_xform(lv["pinion"], deg, hinge_m), MAT["peek"][0], 0.2),
              (_xform(dbox(SPINE), deg, hinge_m), ALU, 0.35),
              (_xform(dbox(HINGE_BLOCK), deg, hinge_m), ALU, 0.35)]
    fixed = [(_xform(dbox(FORK), 0.0, hinge_m), ALU, 0.35), (_xform(dbox(SERVO), 0.0, hinge_m), BLACK, 0.2)]
    top = to_machine(np.array([[0.0, 82.0, CROSS], [0.0, 118.0, CROSS]]), 0.0, hinge_m)
    x0, x1 = sorted(top[:, 0])
    y0, y1 = hinge_m[1] + FORK[0][0] - 6.0, hinge_m[1] + C.HEAD_AHEAD     # to the backboard's face: the head's Z plate
    z0 = top[0, 2]
    fixed += [(box((x0, x1), (y0, y1), (z0, z0 + 8.0)), ALU, 0.35),
              (box((x0, x1), (y1 - 6.0, y1), (z0, z0 + 60.0)), ALU, 0.35)]
    return moving + fixed


def outlet_low(deg):
    """The outlet face's lowest point and its centre (machine offsets from the hinge) at tilt `deg`."""
    ring = np.array([[12.5 * np.cos(a), D.OUTLET[1], D.OUTLET[2] + 12.5 * np.sin(a)]
                     for a in np.linspace(0, 2 * np.pi, 73)])
    o = to_machine(np.vstack([D.OUTLET[None, :], ring]), deg, np.zeros(3))
    return o[1:, 2].min(), o[0]


def hinge_for_cup(xc, yc, deg=DOSE):
    """The hinge position that puts the outlet's centre over cup (xc, yc) with the face RIM_GAP over the rim."""
    low, c = outlet_low(deg)
    return np.array([xc - c[0], yc - c[1], RIM + RIM_GAP - low])


def hinge_for_slot(level, dy=0.0, lift=0.0):
    """The hinge position with the drive clipped onto the cartridge on `level` (dy: in front of it, lift: raised)."""
    return np.array([STACK_OUTLET_X - (HINGE_D[1] - D.OUTLET[1]), STACK_Y - dy, LEVELS[level] + AXIS_DROP + lift])


def cups():
    return [(CUP_X0 + CUP_PITCH * i, CUP_Y0 + CUP_PITCH * j) for j in range(CUP_ROWS) for i in range(CUP_COLS)]


def cup_mesh(x, y):
    outer = cyl((x, y, CUP_H / 2), (0, 0, 1), CUP_OD / 2, CUP_H, res=28)
    bore = cyl((x, y, CUP_H - 1.0), (0, 0, 1), CUP_BORE / 2, 2.2, res=24)
    return outer, bore


def stack(occupied=(True, True, True)):
    """The stack's frame and the stored cartridges. Each shelf holds a cartridge at both ends from behind: a saddle
    under the outlet with a pad on its face, and a fork under the cap; nothing is between, where the clips go."""
    out = []
    x_out = STACK_OUTLET_X
    x_cap = x_out - (287.4 - D.OUTLET[1])               # the cap's end: PR 176's tube is 252 mm, outlet face to cap
    yb = STACK_Y + 26.0
    out.append((box((x_cap - 14.0, x_out + 22.0), (yb, yb + 8.0), (0.0, LEVELS[-1] + 34.0)), ALU, 0.3))   # back wall
    out.append((box((x_cap - 14.0, x_out + 22.0), (STACK_Y + 16.0, yb + 8.0), (0.0, 8.0)), ALU, 0.3))     # foot,
    #                                                       behind the clips: they come within 9 mm of the deck
    for k, z in enumerate(LEVELS):
        out.append((box((x_out - 12.0, x_out + 22.0), (STACK_Y - 4.0, yb), (z - 26.0, z - 13.0)), ALU, 0.3))
        out.append((box((x_out + 1.0, x_out + 5.0), (STACK_Y - 13.0, yb), (z - 14.0, z + 14.0)), (0.2, 0.2, 0.22), 0.2))
        out.append((box((x_cap - 2.0, x_cap + 26.0), (STACK_Y - 4.0, yb), (z - 26.0, z - 15.0)), ALU, 0.3))
        if occupied[k]:
            out += cartridge(LEVEL, hinge_for_slot(k), k)
    return out


def machine(tx, ty, fade=()):
    """cubxl_shuttle's stand-in, without its shuttle, vials, capper and pipette. tx, ty: the head (CubOS frame)."""
    items = []
    fy = C.beam_front(ty)
    add = lambda m, c, s=0.3, o=1.0: items.append((m, c, s, o))
    add(C.deck(), (0.86, 0.90, 0.94), 0.5, 0.55)
    for i, (x0, x1) in enumerate(C.Y_RAILS):
        add(box((x0, x1), (-40, 530), (-50, -2)), ALU)
        add(cyl(((x0 + x1) / 2, 245, -10), (0, 1, 0), 6, 560), STEEL, 0.5)
        for y0 in (-50, 530):
            add(box((x0 - 5, x1 + 5), (y0, y0 + 10), (-55, 30)), BLUE)
    for y0 in (-40, 490):
        add(box((-C.RAIL_GAP, C.DECK[0] + C.RAIL_GAP), (y0, y0 + 40), (-50, -10)), ALU)
    o = 0.22 if "gantry" in fade else 1.0
    for i, ((p0, p1), (r0, r1)) in enumerate(zip(C.PLATE_X, C.Y_RAILS)):
        o0, o1 = (r0 - 14.0, r0 - 4.0) if i == 0 else (r1 + 4.0, r1 + 14.0)
        for q0, q1 in ((p0, p1), (o0, o1)):
            add(box((q0, q1), (fy - 35, fy + 75), (-35, 75)), ALU, 0.3, o)
        lo, hi = min(p0, o0), max(p1, o1)
        add(box((lo, hi), (fy - 10, fy + 50), (75, C.BEAM_UNDER + C.BEAM_TALL)), BLUE, 0.3, o)
    add(box((C.PLATE_X[0][1], C.PLATE_X[1][0]), (fy, fy + C.BEAM_DEPTH),
            (C.BEAM_UNDER, C.BEAM_UNDER + C.BEAM_TALL)), ALU, 0.3, 0.22 if "beam" in fade else 1.0)
    cx = C.REACH0[0] + tx
    bb = fy - (C.BEAM_AHEAD - C.HEAD_AHEAD)
    add(box((cx - 40, cx + 45), (bb + 12, fy), (C.HEAD_UNDER, C.BEAM_UNDER + C.BEAM_TALL + 30)), ALU, 0.3, o)
    add(box((cx - 200, cx + 50), (bb, bb + 10), (150, 330)), BLACK, 0.1, o)
    return items


def rack(filled=None):
    """The rack plate and the 50 cups; `filled` = {cup index: fraction full} shows powder in the bore."""
    xs = [c[0] for c in cups()]
    ys = [c[1] for c in cups()]
    out = [(box((min(xs) - 20, max(xs) + 20), (min(ys) - 20, max(ys) + 20), (0.0, RACK_T)), (0.95, 0.95, 0.96), 0.2)]
    for n, (x, y) in enumerate(cups()):
        outer, bore = cup_mesh(x, y)
        out.append((outer, AL6063, 0.6))
        f = (filled or {}).get(n, 0.0)
        out.append((bore, (0.55, 0.57, 0.62) if f > 0 else (0.15, 0.15, 0.17), 0.1))
    return out


def scene(tx, ty, deg, hinge, carried=None, occupied=(True, True, True), filled=None, fade=("beam",)):
    items = machine(tx, ty, fade)
    items += [(m, c, s, 1.0) for m, c, s in stack(occupied)]
    items += [(m, c, s, 1.0) for m, c, s in rack(filled)]
    items += [(m, c, s, 1.0) for m, c, s in drive(deg, hinge)]
    if carried is not None:
        items += [(m, c, s, 1.0) for m, c, s in cartridge(deg, hinge, carried)]
    return items


def head_for_hinge(h):
    """CubOS (tx, ty) of the head for a hinge at h: the hinge takes the capper's place in x and y."""
    return h[0] - C.REACH0[0], h[1] - C.REACH0[1]


def fit():
    """The numbers the README quotes."""
    low0, c0 = outlet_low(LEVEL)
    low, c = outlet_low(DOSE)
    lv = leaves()
    allp = lambda deg: np.vstack([to_machine(lv[k].points, deg, np.zeros(3)) for k in lv])
    lowest_other = lambda deg: min(to_machine(lv[k].points, deg, np.zeros(3))[:, 2].min()
                                   for k in ("brackets", "stepper", "pinion"))
    hz = [hinge_for_slot(k)[2] for k in range(len(LEVELS))]
    dose_hz = hinge_for_cup(*cups()[0])[2]
    travel_hz = TRAVEL_AXIS + AXIS_DROP
    window = (min(hz + [dose_hz, travel_hz]), max(hz + [dose_hz, travel_hz]))
    p35 = allp(DOSE)
    tips = [hinge_for_cup(x, y) for x, y in cups()]
    heads = [head_for_hinge(t) for t in tips] + [head_for_hinge(hinge_for_slot(0, dy=d)) for d in (0.0, ENGAGE)]
    return dict(outlet_drop=-(low - low0), outlet_dx=c[0] - c0[0], face_over_rim=RIM_GAP,
                centre_over_rim=RIM + RIM_GAP - low + c[2] - RIM, others_over_outlet=lowest_other(DOSE) - low,
                rise_cap=p35[:, 2].max() - low, hinge_window=window, z_span=window[1] - window[0],
                head_x=(min(h[0] for h in heads), max(h[0] for h in heads)),
                head_y=(min(h[1] for h in heads), max(h[1] for h in heads)),
                cap_end_x=min(p35[:, 0]) + tips[0][0], levels=len(LEVELS))


def stream(h, deg=DOSE):
    """Powder falling from the outlet's centre into the cup below it."""
    _, c = outlet_low(deg)
    top = h + c
    return cyl((top[0], top[1], (top[2] + RIM - 8.0) / 2), (0, 0, 1), 1.6, top[2] - RIM + 8.0, res=12)


ISO = np.array([0.75, -1.0, 0.70])                      # front right, above
POWDER = (0.50, 0.52, 0.57)


def pose_items(p):
    """[(mesh, colour, specular, opacity)] for a pose dict: hinge, deg, carried, occupied, filled, pour."""
    tx, ty = head_for_hinge(p["hinge"])
    items = scene(tx, ty, p["deg"], p["hinge"], p.get("carried"), p.get("occupied", (True,) * len(LEVELS)),
                  p.get("filled"), fade=p.get("fade", ("beam",)))
    if p.get("pour"):
        items.append((stream(p["hinge"], p["deg"]), POWDER, 0.1, 1.0))
    return items


def views():
    w, h = 760, 560
    mid = cups()[CUP_COLS * 2 + 4]
    hd = hinge_for_cup(*mid)
    filled = {n: 1.0 for n in range(CUP_COLS * 2 + 4)}
    f = fit()
    dose = dict(hinge=hd, deg=DOSE, carried=0, occupied=(False, True, True), filled=filled, pour=True)
    iso = framed(render(pose_items(dict(dose, fade=("beam", "gantry"))), w, h, 270.0, (215.0, 250.0, 90.0), ISO),
                 "Filling charge cups on the CubXL",
                 ["PR 176's doser on the head, tilting about Y; 3 cartridges stacked at the back;",
                  "50 Al cups (3/4\" × 2.75\", 1/2\" bore) in a rack. Beam see-through"])
    pick = dict(hinge=hinge_for_slot(1), deg=LEVEL, carried=1, occupied=(True, False, True), filled=filled)
    hp = pick["hinge"]
    close = framed(render(pose_items(dict(pick, fade=("beam", "gantry"))), w, h, 125.0,
                          np.array([hp[0] - 60.0, hp[1] - 10.0, hp[2] - 50.0]), np.array([0.55, -1.0, 0.45])),
                   "Clipped onto the middle cartridge",
                   ["the C-clips open towards the stack; the 44T gear meets the NEMA 11's pinion.",
                    "Shelves hold each cartridge at its two ends, from behind"])
    # from the front, the tilt about Y with the heights drawn across
    sc, foc = 150.0, np.array([hd[0] - 40.0, 0.0, 120.0])
    front = render(pose_items(dict(dose, fade=("beam", "gantry"))), w, h, sc, foc, (0.0, -1.0, 0.0))
    d = ImageDraw.Draw(front)
    kz = (h / 2) / sc
    to_px = lambda x, z: (w / 2 + (x - foc[0]) * kz, h / 2 - (z - foc[2]) * kz)
    for z, t, c in ((RIM, f"cup rims {RIM:.0f} mm", (90, 96, 106)),
                    (f["hinge_window"][0], f"hinge, lowest (bottom shelf): {f['hinge_window'][0]:.0f}", (200, 60, 40)),
                    (f["hinge_window"][1], f"hinge, highest: {f['hinge_window'][1]:.0f} "
                                           f"({f['z_span']:.0f} of the 121 mm of Z)", (200, 60, 40))):
        _, pz = to_px(0.0, z)
        for x0 in range(0, w, 14):
            d.line((x0, pz, x0 + 7, pz), fill=c, width=2)
        fnt = font(16, bold=True)
        at = (w - 8, pz + 4 if z == RIM else pz - 4)
        anchor = "ra" if z == RIM else "rb"
        d.rounded_rectangle(d.textbbox(at, t, font=fnt, anchor=anchor), 3, fill=(255, 255, 255))
        d.text(at, t, font=fnt, fill=c, anchor=anchor)
    front = framed(front, "From the front: tilting about Y",
                   [f"at {DOSE:g}° the outlet face is {RIM_GAP:g} mm over the rim, its centre {f['centre_over_rim']:.0f} mm; "
                    f"nothing else", f"comes within {f['others_over_outlet']:.0f} mm of the outlet's height. The cap "
                    f"end rises {f['rise_cap']:.0f} mm above it"])
    top = render(pose_items(dict(dose, fade=("beam", "gantry"))), w, h, 290.0, (240.0, 245.0, 0.0), (0.0, 0.0, 1.0),
                 up=(0.0, 1.0, 0.0))
    d = ImageDraw.Draw(top)
    k = (h / 2) / 290.0
    to_top = lambda x, y: (w / 2 + (x - 240.0) * k, h / 2 - (y - 245.0) * k)
    rx = (C.REACH0[0], C.REACH0[0] + C.TRAVEL[0])
    ry = (C.REACH0[1], C.REACH0[1] + C.TRAVEL[1])
    (a, b), (c_, e) = to_top(rx[0], ry[1]), to_top(rx[1], ry[0])
    d.rectangle((a, b, c_, e), outline=(64, 128, 230), width=3)
    d.text((a + 6, e - 26), "the hinge's reach (the capper's, 388 × 234 mm)", font=font(16, bold=True),
           fill=(40, 90, 180))
    top = framed(top, "From above", ["the stack at the back, the rack in front; front of the machine at the bottom",
                                     "the cartridge overhangs the deck's left edge when filling the left columns"])
    gap = 12
    sheet = Image.new("RGB", (2 * iso.width + 3 * gap, 2 * iso.height + 3 * gap), (232, 234, 238))
    for i, im in enumerate((iso, close, front, top)):
        sheet.paste(im, (gap + (i % 2) * (iso.width + gap), gap + (i // 2) * (iso.height + gap)))
    sheet.save(HERE / "alloy_cubxl_views.png", optimize=True)
    print("alloy_cubxl_views.png", sheet.size)


def ease(a, b, n):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return [a + (b - a) * (1 - np.cos(np.pi * i / max(n - 1, 1))) / 2 for i in range(n)]


def sequence():
    """[(pose, caption)]: pick 4047 from the bottom shelf, fill two cups, put it back, pick Si, top up the first."""
    seq = []
    occ = [True, True, True]
    filled = {}
    rest = hinge_for_slot(2, dy=ENGAGE + 20.0) + np.array([0.0, 0.0, 0.0])
    add = lambda h, deg, cap, carried=None, pour=False: seq.append(
        (dict(hinge=np.asarray(h, float), deg=deg, carried=carried, occupied=tuple(occ), filled=dict(filled),
              pour=pour), cap))
    for _ in range(3):
        add(rest, LEVEL, "Ready: three powders in the stack, 50 empty cups")
    for h in ease(rest, hinge_for_slot(0, dy=ENGAGE), 6):
        add(h, LEVEL, "To the bottom shelf (4047), level, in front of it")
    for h in ease(hinge_for_slot(0, dy=ENGAGE), hinge_for_slot(0), 5):
        add(h, LEVEL, "In along +Y: the tube snaps into the clips, the gear meets the pinion")
    occ[0] = False
    for h in ease(hinge_for_slot(0), hinge_for_slot(0, lift=5.0), 2):
        add(h, LEVEL, "Up 5 mm, off the shelf", 0)
    for h in ease(hinge_for_slot(0, lift=5.0), hinge_for_slot(0, dy=ENGAGE, lift=5.0), 5):
        add(h, LEVEL, "Out along -Y, carrying the cartridge", 0)
    prev = hinge_for_slot(0, dy=ENGAGE, lift=5.0)
    for n in (0, 1):
        tgt = hinge_for_cup(*cups()[n])
        above = hinge_for_cup(*cups()[n], deg=LEVEL)
        above[2] = TRAVEL_AXIS + AXIS_DROP
        for h in ease(prev, above, 7 if n == 0 else 4):
            add(h, LEVEL, f"Level, over the rims, to cup {n + 1}", 0)
        for a, h in zip(ease(LEVEL, DOSE, 5), ease(above, tgt, 5)):
            add(h, float(a), f"Tilt about Y to {DOSE:g}° and down: outlet {RIM_GAP:g} mm over the rim", 0)
        for i in range(4):
            filled[n] = (i + 1) / 4
            add(tgt, DOSE, f"Fill cup {n + 1} with 4047, closing the loop on the balance", 0, pour=i < 3)
        for a, h in zip(ease(DOSE, LEVEL, 4), ease(tgt, above, 4)):
            add(h, float(a), "Back to level", 0)
        prev = above
    for h in ease(prev, hinge_for_slot(0, dy=ENGAGE, lift=5.0), 7):
        add(h, LEVEL, "Back to the stack", 0)
    for h in ease(hinge_for_slot(0, dy=ENGAGE, lift=5.0), hinge_for_slot(0, lift=5.0), 4):
        add(h, LEVEL, "In over the bottom shelf", 0)
    occ[0] = True
    for h in ease(hinge_for_slot(0, lift=5.0), hinge_for_slot(0), 2):
        add(h, LEVEL, "Down onto the shelf")
    for h in ease(hinge_for_slot(0), hinge_for_slot(0, dy=ENGAGE), 4):
        add(h, LEVEL, "Out along -Y: the clips let go")
    for h in ease(hinge_for_slot(0, dy=ENGAGE), hinge_for_slot(1, dy=ENGAGE), 3):
        add(h, LEVEL, "Up to the middle shelf (Si)")
    for h in ease(hinge_for_slot(1, dy=ENGAGE), hinge_for_slot(1), 4):
        add(h, LEVEL, "Clip on to the Si cartridge")
    occ[1] = False
    for h in ease(hinge_for_slot(1), hinge_for_slot(1, lift=5.0), 2):
        add(h, LEVEL, "Up 5 mm, off the shelf", 1)
    for h in ease(hinge_for_slot(1, lift=5.0), hinge_for_slot(1, dy=ENGAGE, lift=5.0), 4):
        add(h, LEVEL, "Out along -Y, carrying the Si cartridge", 1)
    tgt = hinge_for_cup(*cups()[0])
    above = hinge_for_cup(*cups()[0], deg=LEVEL)
    above[2] = TRAVEL_AXIS + AXIS_DROP
    for h in ease(hinge_for_slot(1, dy=ENGAGE, lift=5.0), above, 6):
        add(h, LEVEL, "Back to cup 1", 1)
    for a, h in zip(ease(LEVEL, DOSE, 4), ease(above, tgt, 4)):
        add(h, float(a), f"Tilt to {DOSE:g}°", 1)
    for i in range(3):
        add(tgt, DOSE, "Add Si to cup 1: a second powder in the same cup", 1, pour=True)
    for a, h in zip(ease(DOSE, LEVEL, 3), ease(tgt, above, 3)):
        add(h, float(a), "Back to level; 48 cups to go", 1)
    for _ in range(3):
        add(above, LEVEL, "Back to level; 48 cups to go", 1)
    return seq


def _frame(args):
    pose, cap, w, h = args
    im = render(pose_items(dict(pose, fade=("beam", "gantry"))), w, h, 250.0, (190.0, 235.0, 95.0), ISO)
    im = framed(im, "Plan B: filling Al charge cups (concept)", [cap], head=70)
    return im.convert("P", palette=Image.ADAPTIVE, colors=128)


def motion(w=640, h=450, procs=4):
    from multiprocessing import Pool
    seq = sequence()
    with Pool(procs) as pool:
        frames = pool.map(_frame, [(p, c, w, h) for p, c in seq])
    out = HERE / "alloy_cubxl.gif"
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=150, loop=0, optimize=True)
    print("alloy_cubxl.gif", len(frames), "frames", out.stat().st_size, "bytes")


if __name__ == "__main__":
    print({k: (np.round(v, 1) if not isinstance(v, int) else v) for k, v in fit().items()})
    if "--fit" not in sys.argv:
        views()
        if "--views" not in sys.argv:
            motion()

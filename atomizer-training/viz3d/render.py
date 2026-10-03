"""Two hero stills of the rePowder model, 1600 x 900: the whole machine, and a section through
furnace, chamber and container.

    xvfb-run -a -s "-screen 0 1920x1080x24" python render.py           # -> out/machine.png, out/section.png, out/compare.png
    xvfb-run -a -s "-screen 0 1920x1080x24" python render.py compare   # only the model-vs-video comparison
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

import model as M
from scene import OUT, Scene, font, load_machine

HERE = Path(__file__).resolve().parent

SIZE = (1600, 900)


MACHINE_CAM = [(-1650, -3900, 2150), (170, 330, 820), (0, 0, 1)]


def auto_place(sc, items, top=0.09, bottom=0.88, split=0.45):
    """Put each label on the side nearest its anchor and order each side by the anchor's screen
    height, so no two leader lines on a side cross. items: [(text, xyz)]."""
    sc.render_base()
    pts = [(t, xyz, sc.project(xyz)) for t, xyz in items]
    out = []
    for side, fx in (([p for p in pts if p[2][0] < split], 0.025), ([p for p in pts if p[2][0] >= split], 0.975)):
        side.sort(key=lambda p: p[2][1])
        if not side:
            continue
        need = [0.028 + 0.024 * t.count("\n") for t, _, _ in side]      # half-heights, as fractions
        ys = []
        for (t, _, (px, py)), h in zip(side, need):
            y = min(max(py, top + h), bottom - h)
            if ys:
                y = max(y, ys[-1][0] + ys[-1][1] + h + 0.012)
            ys.append((y, h))
        over = ys[-1][0] + ys[-1][1] - bottom
        if over > 0:
            ys[-1] = (ys[-1][0] - over, ys[-1][1])
            for i in range(len(ys) - 2, -1, -1):
                lim = ys[i + 1][0] - ys[i + 1][1] - ys[i][1] - 0.012
                ys[i] = (min(ys[i][0], lim), ys[i][1])
        # leader lines start at the box edge facing the anchor; swap neighbours until no two lines cross
        W, H = sc.size
        sc_ = max(W / 1280, 0.8)
        f = font(14 * sc_)
        slots = [y for y, _ in ys]
        order = list(range(len(side)))

        def seg(k, slot):
            t, _, (px, py) = side[k]
            tw = max(f.getlength(line) for line in t.split("\n")) + 12 * sc_
            x0 = fx * W + (tw if fx < 0.5 else -tw)
            return (x0, slot * H), (px * W, py * H)

        def crosses(a, b):
            (p1, p2), (p3, p4) = a, b

            def ccw(A, B, C):
                return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
            return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)
        for _ in range(len(side) ** 2):
            swapped = False
            for i in range(len(order) - 1):
                for j in range(i + 1, len(order)):
                    if crosses(seg(order[i], slots[i]), seg(order[j], slots[j])):
                        order[i], order[j] = order[j], order[i]
                        swapped = True
            if not swapped:
                break
        for k, y in zip(order, slots):
            out.append((side[k][0], side[k][1], (fx, y), 1.0))
    return out


MACHINE_LABELS = [
    ("furnace lid (bell): hinges up to the left;\nwindow + HOT label, black knob", (-40, -105, 1440)),
    ("furnace body: coil, crucible, insulation", (-125, -55, 1250)),
    ("melting control panel (GU 500)", tuple(M.PANEL_C)),
    ("15.6 in HMI on a swing arm", tuple(M.HMI_C + np.array([0, -20, 60]))),
    ("main switch", tuple(M.SWITCH_C)),
    ("blue frame: induction generator, PLC and\npneumatics built in (side doors)", (M.FR_X[0] + 40, M.FR_Y[0], 1500)),
    ("atomization chamber, 57 L:\nsloped underside to the outlet", (200, M.CH_Y[0], 820)),
    ("view port", tuple(M.VIEWPORT + M.VIEWPORT_N * 40)),
    ("door (3 star knobs) carries the ultrasonic unit", (M.CH_X[0] - 20, -60, 1000)),
    ("transducer under its protective cover", tuple(M.PLATE_C - M.STACK_DIR * 330 + np.array([0, -50, 0]))),
    ("cone, valve", (M.CHUTE_X - 60, -80, 360)),
    ("powder container, flange clamp", (M.CHUTE_X - 40, -60, 180)),
    ("argon 5N + regulator", (-560, 650, 1100)),
    ("compressed-air filter-regulator", (-275, 960, 1460)),
    ("vacuum pump", (-700, 120, 200)),
    ("heat exchanger (chilled water)", (920, 140, 820)),
]


def machine():
    sc = Scene("machine", "AMAZEMET rePowder induction atomizer (BYU): CAD model", size=SIZE, gif=False, mp4=False)
    load_machine(sc)
    sc.cam = MACHINE_CAM
    sc.caption = ("Proportions are read off the training videos; the crucible is scaled from the vendor drawing "
                  "(see README: measured vs. assumed).")
    sc.labels = auto_place(sc, MACHINE_LABELS)
    img = sc.snap()
    img.convert("RGB").save(OUT / "machine.png", optimize=True)
    sc.pl.close()
    print("wrote out/machine.png")


def machine_clean():
    """Artwork for title cards: no text at all, the machine in the right 60 % of a white 1600 x 900."""
    from PIL import Image
    sc = Scene("machine_clean", "", size=(960, 900), gif=False, mp4=False)
    load_machine(sc, hide=("floor",))
    sc.cam = MACHINE_CAM
    sc.view_angle = 27
    img = sc.snap()
    sc.pl.close()
    canvas = Image.new("RGB", SIZE, "white")
    canvas.paste(img.convert("RGB"), (SIZE[0] - 960, 0))
    canvas.save(OUT / "machine_clean.png", optimize=True)
    print("wrote out/machine_clean.png")


UTILITIES = ("argon_cylinder", "argon_regulator", "argon_gauges", "vacuum_pump", "pump_sight_glass", "heat_exchanger",
             "hx_grille", "hx_display", "air_frl", "floor", "hmi", "hmi_screen", "hmi_widgets", "hmi_arm")


def section_panel(size, cam, labels, view_angle=30.0):
    sc = Scene("section", "", size=size, gif=False, mp4=False)
    load_machine(sc, cut="all", hide=UTILITIES + ("slug1", "slug2", "slug3"), ghost={"stack_cover": 0.22},
                 pipes=False)
    sc.cam = cam
    sc.view_angle = view_angle
    sc.labels = [(t, xyz, at, 1.0) for t, xyz, at in labels]
    img = sc.snap()
    sc.pl.close()
    return img


def section():
    """Two panels: the whole column cut at the furnace axis, and the furnace close up."""
    a = np.radians(M.TC_ANGLE)
    tc_run = np.array([0, 0, M.BODY_TOP + 6]) + np.array([np.cos(a), np.sin(a), 0]) * 80
    left = section_panel((800, 900), [(-700, -2500, 1000), (40, 0, 830), (0, 0, 1)], [
        ("furnace", (60, 0, 1250), (0.06, 0.12)),
        ("atomization chamber\n(57 L, argon)", (-100, 60, 1060), (0.06, 0.27)),
        ("plate (Ti, 20 x 100)", tuple(M.PLATE_C + M.PLATE_UP * 30), (0.70, 0.33)),
        ("sonotrode", tuple(M.PLATE_C - M.STACK_DIR * 80), (0.06, 0.42)),
        ("booster (1.5:1)", tuple(M.PLATE_C - M.STACK_DIR * 215), (0.06, 0.52)),
        ("transducer (40 kHz),\nunder its cover", tuple(M.PLATE_C - M.STACK_DIR * 310), (0.06, 0.62)),
        ("splash plate,\ncatch bowl", (M.CHUTE_X - 10, 0, 610), (0.70, 0.45)),
        ("45° underside:\npowder slides to the outlet", (60, 0, M.chamber_floor(60)), (0.70, 0.56)),
        ("cone, valve, flange clamp", (M.CHUTE_X + 50, 0, 330), (0.70, 0.66)),
        ("powder container", (M.CHUTE_X + M.CONT_R - 2, 0, 160), (0.70, 0.78)),
    ], view_angle=36)
    right = section_panel((800, 900), [(-330, -820, 1430), (5, 0, 1262), (0, 0, 1)], [
        ("furnace bell (lid)", (-70, 60, M.HOOD_Z0 + 110), (0.06, 0.135)),
        ("wall thermocouple\n(Type N)", tuple(tc_run), (0.06, 0.22)),
        ("top insulation\n(filling cone)", (-75, 0, M.BODY_TOP - 18), (0.06, 0.33)),
        ("graphite crucible:\nØ57 bore, 36° cone\nfloor to the pour hole", (-33, 0, M.Z_CR + 30), (0.06, 0.48)),
        ("induction coil\n(10 kW, 7 kHz)", (-47, 0, M.Z_CR - 28 + 12.5 * 2.5), (0.06, 0.64)),
        ("nozzle (Ø0.5 mm;\n0.7 for Al), white\nside up", (-5, 0, M.CRUCIBLE_BASE - 2.5), (0.06, 0.80)),
        ("rod adapter,\nholder arm", (40, 18, M.RIM + M.ARM_ABOVE_RIM + 8), (0.74, 0.17)),
        ("charge: 6063 rod\nØ17 x 100 (1 of 4)", (-5, 19, M.Z_CR + 60), (0.74, 0.85)),
        ("sealing rod\n(seated)", (0, 0, M.Z_CR + 55), (0.74, 0.32)),
        ("side insulation", (40.5, 0, M.Z_CR + 50), (0.74, 0.45)),
        ("bottom insulation", (60, 0, M.CRUCIBLE_BASE - 12), (0.74, 0.62)),
        ("nozzle holder; thin graphite\nnut under the top plate", (25, 0, 1120), (0.74, 0.72)),
    ], view_angle=30)
    from PIL import Image, ImageDraw
    from scene import font
    W, H = 1600, 900
    img = Image.new("RGB", (W, H), "white")
    img.paste(left.convert("RGB"), (0, 0))
    img.paste(right.convert("RGB"), (800, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.line([(800, 60), (800, 780)], fill=(200, 204, 210), width=2)
    d.rectangle((0, 0, W, 40), fill=(255, 255, 255, 255))
    d.line([(0, 40), (W, 40)], fill=(200, 204, 210), width=1)
    d.text((14, 10), "rePowder: section at the furnace axis (front half removed)", font=font(19, bold=True),
           fill=(20, 20, 24))
    d.rounded_rectangle((808, 50, 990, 76), 5, fill=(255, 255, 255, 235), outline=(120, 124, 130))
    d.text((816, 54), "furnace, close up", font=font(15, bold=True), fill=(30, 34, 40))
    cap = ("Argon over-pressure pushes the melt through the nozzle when the sealing rod lifts; it falls onto the plate "
           "vibrating at 40 kHz, and the droplets freeze into powder that drops through the cone into the container.")
    fc = font(18)
    lines, cur = [], ""
    for w in cap.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fc) > W - 60 and cur:
            lines.append(cur)
            cur = w
        else:
            cur = t
    lines.append(cur)
    h = len(lines) * 24 + 20
    d.rectangle((0, H - h - 8, W, H), fill=(255, 255, 255, 235))
    d.line([(0, H - h - 8), (W, H - h - 8)], fill=(30, 60, 140, 255), width=2)
    for i, t in enumerate(lines):
        d.text((30, H - h + 2 + i * 24), t, font=fc, fill=(15, 15, 20))
    img.save(OUT / "section.png", optimize=True)
    print("wrote out/section.png")


COMPARE = [   # (reference frame in ref/, camera roughly matching it, view angle)
    ("front_9kn-HhXCr1o_25m00s.jpg", [(40, -1650, 780), (40, 0, 760), (0, 0, 1)], 30),
    ("left_58wJ_Khwgyk_77m00s.jpg", [(-1150, -850, 1080), (-90, 0, 830), (0, 0, 1)], 30),
    ("frontleft_FDRTt68Vfvo_51m00s.jpg", [(-520, -1150, 1380), (30, 0, 980), (0, 0, 1)], 30),
]


def compare():
    """The model next to frames of the real machine from about the same viewpoints (out/compare.png)."""
    from PIL import Image, ImageDraw
    from scene import font
    tiles = []
    for ref, cam, va in COMPARE:
        frame = Image.open(HERE / "ref" / ref).convert("RGB")
        w, h = frame.size
        sc = Scene("compare", "", size=(w - w % 2, h - h % 2), gif=False, mp4=False)
        load_machine(sc, hide=("floor",), pipes=False)
        sc.cam = cam
        sc.view_angle = va
        img = sc.snap().convert("RGB")
        sc.pl.close()
        tiles.append((frame, img, ref))
    th = 360
    row = []
    for frame, img, ref in tiles:
        f = frame.resize((int(frame.width * th / frame.height), th))
        m = img.resize((int(img.width * th / img.height), th))
        row.append((f, m, ref))
    W = max(f.width + m.width for f, m, _ in row) + 30
    H = len(row) * (th + 34) + 50
    out = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(out)
    d.text((10, 10), "Training-video frames (left) and the CAD model from about the same viewpoint (right)",
           font=font(18, bold=True), fill=(20, 20, 24))
    y = 46
    for f, m, ref in row:
        out.paste(f, (10, y)); out.paste(m, (20 + f.width, y))
        vid, at = ref.split("_", 1)[1].replace(".jpg", "").rsplit("_", 1)
        d.text((12, y + th + 4), f"{vid} at {at}", font=font(14), fill=(60, 60, 66))
        y += th + 34
    out.save(OUT / "compare.png", optimize=True)
    print("wrote out/compare.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    if sys.argv[1:] == ["compare"]:
        compare()
        sys.exit()
    machine()
    machine_clean()
    section()
    compare()

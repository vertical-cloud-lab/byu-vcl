"""Draw the measurement guide: each training-video frame with the measurements marked on it, and a legend below.

    python make_guide.py        # writes N_*.jpg next to this file

The frames are in ../frames/. The text of every measurement is in sheets.py; the marks are placed here in frame
pixels. Sheet 4 is a drawn side view of the front port, for the depths and the angle a photo can't show.
"""
from __future__ import annotations

import csv
import math
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from sheets import PRIORITY, SHEETS

HERE = Path(__file__).resolve().parent
FRAMES = HERE.parent / "frames"
W = 1280
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
PALETTE = ["#FFD400", "#00E5FF", "#FF4FD8", "#7CFF4F", "#FF9A1F", "#B69CFF", "#FF6B6B", "#5AB4FF"]
PRI_COLOUR = {1: "#E0393E", 2: "#2F7DE1", 3: "#6B7280"}
PRI_WORD = {1: "FIRST", 2: "NEXT", 3: "IF TIME"}


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else REG, size)


# ---------------------------------------------------------------- marks drawn on the photo, in frame pixels
# ("dim", id, p1, p2[, tag_at])      double-headed arrow between two points, tagged
# ("call", id, point, tag_at)        leader from a point to a tag
# ("part", text, point, label_at)    names a part of the machine (white label)
# ("ext", p1, p2)                    thin dashed extension line
# ("note", id, text, at)             short note in the tag's colour
MARKS = {
    "1_front_cover_on": [
        ("ext", (462, 236), (462, 615)),
        ("ext", (588, 293), (770, 293)),
        ("ext", (588, 293), (588, 356)),
        ("dim", "F1", (470, 316), (702, 316), (510, 316)),
        ("dim", "F2", (505, 480), (632, 480), (568, 480)),
        ("dim", "F2", (652, 402), (652, 466), (690, 434)),
        ("call", "F3", (560, 432), (400, 470)),
        ("dim", "F4", (463, 352), (587, 352), (525, 352)),
        ("dim", "F5", (770, 293), (770, 714), (770, 600)),
        ("note", "F5", "to the floor", (785, 680)),
        ("call", "F6", (468, 214), (330, 150)),
        ("call", "F7", (452, 330), (300, 270)),
        ("part", "grey LED cover, 12 sides", (665, 236), (820, 165)),
        ("part", "cable pod", (600, 452), (850, 520)),
        ("part", "top-left door clamp (star knob)", (410, 345), (30, 395)),
        ("part", "furnace foot bracket", (440, 190), (170, 95)),
        ("part", "chamber's left edge", (462, 560), (190, 560)),
    ],
    "2_front_cover_closeup": [
        ("dim", "F8", (594, 250), (1004, 250), (700, 250)),
        ("dim", "F10", (648, 318), (876, 318), (762, 318)),
        ("call", "F9", (760, 390), (1010, 600)),
        ("note", "F9", "rule end on the glass (sheet 4)", (840, 645)),
        ("part", "cover's front face", (450, 360), (120, 640)),
        ("part", "LED ring", (900, 330), (1000, 420)),
        ("part", "glass", (700, 420), (520, 560)),
    ],
    "3_front_cover_off": [
        ("dim", "F12", (585, 124), (792, 366), (640, 190)),
        ("call", "F13", (575, 262), (380, 170)),
        ("note", "F13", "chamber face to nut face (sheet 4)", (210, 225)),
        ("call", "F14", (735, 345), (900, 470)),
        ("note", "F14", "phone flat on the nut face", (850, 515)),
        ("call", "F15", (785, 300), (1010, 380)),
        ("part", "shiny nut: leave it alone", (612, 330), (760, 610)),
    ],
    "5_left_sight_glass": [
        ("ring", (645, 80), 44),
        ("note", "L1", "the small window: L1 to L5 (side view in the inset)", (700, 150)),
        ("call", "L7", (622, 196), (520, 240)),
        ("part", "door (left side of the chamber)", (720, 380), (700, 560)),
        ("part", "ultrasonic stack", (470, 400), (300, 560)),
        ("part", "top door clamp", (715, 92), (1000, 230)),
    ],
    "6_lid_window": [
        ("dim", "T1", (458, 560), (874, 560), (666, 560)),
        ("dim", "T2", (520, 229), (520, 688), (520, 610)),
        ("dim", "T3", (262, 182), (1058, 182), (380, 182)),
        ("dim", "T4", (1110, 22), (1110, 714), (1110, 300)),
        ("note", "T4", "plate continues below", (1000, 680)),
        ("dim", "T5", (310, 125), (662, 125), (486, 125)),
        ("call", "T6", (436, 430), (140, 330)),
    ],
    "7_lid_from_front": [
        ("call", "T7", (600, 322), (930, 400)),
        ("note", "T7", "phone flat on the plate", (880, 445)),
        ("dim", "T8", (535, 188), (535, 714), (535, 520)),
        ("note", "T8", "to the floor", (550, 680)),
        ("dim", "T9", (80, 452), (820, 452), (300, 452)),
        ("note", "T9", "tape round the lid here", (110, 490)),
        ("call", "T10", (520, 14), (260, 90)),
        ("call", "T11", (40, 420), (170, 620)),
        ("part", "window plate, 8 screws", (380, 40), (90, 175)),
        ("part", "lid hinge", (35, 380), (120, 300)),
    ],
    "8_whole_machine": [
        ("dim", "M1", (764, 690), (998, 690), (880, 690)),
        ("note", "M1", "tape round the body", (770, 735)),
        ("dim", "M2", (1250, 795), (1250, 1076), (1250, 940)),
        ("dim", "M3", (1385, 285), (1385, 1076), (1385, 470)),
        ("note", "M3", "to the floor", (1405, 1035)),
        ("call", "M4", (1100, 312), (1060, 190)),
        ("call", "M5", (1003, 610), (1090, 690)),
        ("call", "M6", (603, 352), (420, 330)),
        ("call", "M6", (592, 440), (420, 330)),
        ("part", "lid, open", (700, 470), (230, 470)),
        ("part", "blue cabinet", (900, 400), (850, 220)),
        ("part", "chamber top", (1150, 760), (1500, 800)),
    ],
}

SCALE = {"8_whole_machine": W / 1920}


def colour_map(rows):
    return {r[0]: PALETTE[i % len(PALETTE)] for i, r in enumerate(rows)}


def _poly_outline(d, pts, fill):
    d.polygon(pts, fill=fill, outline="black")


def arrow(d, p1, p2, col, width=4):
    (x1, y1), (x2, y2) = p1, p2
    d.line([p1, p2], fill="black", width=width + 4)
    d.line([p1, p2], fill=col, width=width)
    ang = math.atan2(y2 - y1, x2 - x1)
    for (tx, ty), a in (((x2, y2), ang), ((x1, y1), ang + math.pi)):
        L, Wd = 16, 8
        bx, by = tx - L * math.cos(a), ty - L * math.sin(a)
        pts = [(tx, ty), (bx + Wd * math.sin(a), by - Wd * math.cos(a)), (bx - Wd * math.sin(a), by + Wd * math.cos(a))]
        _poly_outline(d, pts, col)


def tag(d, at, text, col, size=26):
    f = font(size, True)
    l, t, r, b = d.textbbox((0, 0), text, font=f)
    w, h = r - l + 16, b - t + 12
    x, y = at[0] - w / 2, at[1] - h / 2
    d.rounded_rectangle([x, y, x + w, y + h], radius=8, fill=col, outline="black", width=3)
    d.text((x + 8 - l, y + 6 - t), text, font=f, fill="black")


def label(d, at, text, fg="black", bg="white", size=20, bold=True):
    f = font(size, bold)
    l, t, r, b = d.textbbox((0, 0), text, font=f)
    x, y = at
    d.rounded_rectangle([x - 6, y - 4, x + r - l + 6, y + b - t + 6], radius=5, fill=bg, outline="black", width=2)
    d.text((x - l, y - t), text, font=f, fill=fg)
    return x + (r - l) / 2, y + (b - t) / 2


def dashed(d, p1, p2, col="white", dash=10):
    (x1, y1), (x2, y2) = p1, p2
    n = max(1, int(math.hypot(x2 - x1, y2 - y1) / dash))
    for i in range(0, n, 2):
        a, b = i / n, min(1, (i + 1) / n)
        seg = [(x1 + (x2 - x1) * a, y1 + (y2 - y1) * a), (x1 + (x2 - x1) * b, y1 + (y2 - y1) * b)]
        d.line(seg, fill="black", width=5)
        d.line(seg, fill=col, width=2)


def draw_marks(im, marks, cols, s=1.0):
    d = ImageDraw.Draw(im)
    S = lambda p: (p[0] * s, p[1] * s)
    later = []
    for m in marks:
        kind = m[0]
        if kind == "ext":
            dashed(d, S(m[1]), S(m[2]))
        elif kind == "dim":
            _, mid, p1, p2, *rest = m
            arrow(d, S(p1), S(p2), cols[mid])
            at = S(rest[0]) if rest else ((p1[0] + p2[0]) * s / 2, (p1[1] + p2[1]) * s / 2)
            later.append(("tag", at, mid))
        elif kind == "call":
            _, mid, pt, at = m
            pt, at = S(pt), S(at)
            d.line([pt, at], fill="black", width=6)
            d.line([pt, at], fill=cols[mid], width=3)
            d.ellipse([pt[0] - 7, pt[1] - 7, pt[0] + 7, pt[1] + 7], fill=cols[mid], outline="black", width=2)
            later.append(("tag", at, mid))
        elif kind == "part":
            _, text, pt, at = m
            pt, at = S(pt), S(at)
            later.append(("part", pt, at, text))
        elif kind == "note":
            _, mid, text, at = m
            later.append(("note", S(at), mid, text))
        elif kind == "ring":
            _, c, r = m
            c = S(c)
            d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], outline="black", width=9)
            d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], outline="#FFD400", width=5)
    for it in later:  # labels last, so lines never cross them
        if it[0] == "part":
            _, pt, at, text = it
            f = font(20, True)
            l, t, r, b = d.textbbox((0, 0), text, font=f)
            cx, cy = at[0] + (r - l) / 2, at[1] + (b - t) / 2
            d.line([pt, (cx, cy)], fill="black", width=4)
            d.line([pt, (cx, cy)], fill="white", width=2)
            d.ellipse([pt[0] - 5, pt[1] - 5, pt[0] + 5, pt[1] + 5], fill="white", outline="black", width=2)
    for it in later:
        if it[0] == "part":
            label(d, it[2], it[3], fg="black", bg="white", size=20)
        elif it[0] == "note":
            _, at, mid, text = it
            label(d, at, text, fg="black", bg=cols[mid], size=19)
    for it in later:
        if it[0] == "tag":
            tag(d, it[1], it[2], cols[it[2]])


def legend(rows, cols, width=W, pad=22):
    """Rows of the legend, two columns, as an image."""
    colw = (width - 3 * pad) // 2
    ft, fb, fs = font(23, True), font(19), font(19, True)
    blocks = []
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    for mid, pri, title, how, guess, var in rows:
        lines = textwrap.wrap(how, width=int(colw / 10.6))
        guess_w = tmp.textlength(f"now in the model: {guess}", font=fs) + 24 + tmp.textlength("measured:", font=fs)
        h = 36 + 25 * len(lines) + 34 + 10 + (28 if guess_w + 130 > colw else 0)
        blocks.append((h, mid, pri, title, lines, guess, var))
    # fill the left column first, then the right, keeping order
    total = sum(b[0] for b in blocks)
    left, acc = [], 0
    for b in blocks:
        if acc + b[0] / 2 <= total / 2 or not left:
            left.append(b)
            acc += b[0]
        else:
            break
    right = blocks[len(left):]
    H = max(sum(b[0] for b in left), sum(b[0] for b in right) if right else 0) + pad
    im = Image.new("RGB", (width, H), "#F4F4F2")
    d = ImageDraw.Draw(im)
    for ci, colblocks in enumerate((left, right)):
        x0, y = pad + ci * (colw + pad), pad // 2
        for h, mid, pri, title, lines, guess, var in colblocks:
            tag(d, (x0 + 30, y + 17), mid, cols[mid], size=22)
            d.text((x0 + 66, y + 4), title, font=ft, fill="black")
            tw = d.textlength(title, font=ft)
            pw = d.textlength(PRI_WORD[pri], font=font(14, True)) + 14
            px = x0 + colw - pw
            d.rounded_rectangle([px, y + 8, px + pw, y + 29], radius=6, fill=PRI_COLOUR[pri])
            d.text((px + 7, y + 11), PRI_WORD[pri], font=font(14, True), fill="white")
            yy = y + 36
            for ln in lines:
                d.text((x0 + 10, yy), ln, font=fb, fill="#222222")
                yy += 25
            d.text((x0 + 10, yy + 4), f"now in the model: {guess}", font=fs, fill="#555555")
            gx = x0 + 10 + d.textlength(f"now in the model: {guess}", font=fs) + 24
            if gx + d.textlength("measured:", font=fs) + 120 > x0 + colw:   # no room: next line
                yy += 28
                gx = x0 + 10
            d.text((gx, yy + 4), "measured:", font=fs, fill="black")
            lx = gx + d.textlength("measured:", font=fs) + 8
            d.line([(lx, yy + 26), (x0 + colw - 8, yy + 26)], fill="black", width=2)
            y += h
            d.line([(x0, y - 5), (x0 + colw, y - 5)], fill="#D0D0CC", width=1)
    return im


def header(title, where, src, width=W):
    ft, fw, fsrc = font(34, True), font(21), font(16)
    lines = textwrap.wrap(where, width=105)
    H = 62 + 28 * len(lines) + 12
    im = Image.new("RGB", (width, H), "#1E2A38")
    d = ImageDraw.Draw(im)
    d.text((22, 14), title, font=ft, fill="white")
    s = f"frame: {src}"
    d.text((width - 22 - d.textlength(s, font=fsrc), 26), s, font=fsrc, fill="#B8C4D0")
    y = 62
    for ln in lines:
        d.text((22, y), ln, font=fw, fill="#E8EEF4")
        y += 28
    return im


def footer(width=W):
    im = Image.new("RGB", (width, 74), "#1E2A38")
    d = ImageDraw.Draw(im)
    f = font(18)
    x = 22
    for p in (1, 2, 3):
        pw = d.textlength(PRI_WORD[p], font=font(14, True)) + 14
        d.rounded_rectangle([x, 11, x + pw, 32], radius=6, fill=PRI_COLOUR[p])
        d.text((x + 7, 14), PRI_WORD[p], font=font(14, True), fill="white")
        x += pw + 8
        t = PRIORITY[p] + "     "
        d.text((x, 12), t, font=f, fill="white")
        x += d.textlength(t, font=f)
    d.text((22, 44), "Millimetres and degrees. A phone photo of the tape in place, for each one, lets us check it.",
           font=font(17), fill="#B8C4D0")
    return im


def stack(*ims, width=W):
    H = sum(i.height for i in ims)
    out = Image.new("RGB", (width, H), "white")
    y = 0
    for i in ims:
        out.paste(i, (0, y))
        y += i.height
    return out


def left_port_photo():
    """58wJ 77:25, with the side-on 9kn-HhXCr1o 25:06 view of the same window as an inset."""
    im = Image.open(FRAMES / "left_port_58wJ_Khwgyk_7725.jpg").convert("RGB")
    side = Image.open(FRAMES / "left_port_9kn-HhXCr1o_2506.jpg").convert("RGB").crop((480, 0, 640, 190))
    k = 2.6
    side = side.resize((int(side.width * k), int(side.height * k)), Image.LANCZOS)
    d = ImageDraw.Draw(side)
    # in the inset (source x 480.., y 0..): ring outer face ~x 538, door face ~x 580; ring top ~y 38, bottom ~y 112
    T = lambda x, y: ((x - 480) * k, y * k)
    cols = colour_map(next(s for s in SHEETS if s["key"] == "5_left_sight_glass")["rows"])
    arrow(d, T(538, 128), T(581, 128), cols["L2"])
    tag(d, T(560, 146), "L2", cols["L2"], size=22)
    arrow(d, T(527, 37), T(527, 113), cols["L1"])
    tag(d, T(510, 75), "L1", cols["L1"], size=22)
    label(d, (8, side.height - 40), "same window, side on", size=18)
    frame = Image.new("RGB", (side.width + 8, side.height + 8), "white")
    frame.paste(side, (4, 4))
    im.paste(frame, (12, 12))
    return im


def front_side_sketch(cols):
    """Side view of the front port: (a) cover off, (b) cover on. Chamber face on the right, operator on the left."""
    Wd, Hd = W, 780
    im = Image.new("RGB", (Wd, Hd), "#2B3540")
    d = ImageDraw.Draw(im)
    k = 2.2  # px per mm

    def panel(x_face, oy, cover):
        P = lambda s, r: (x_face - k * s, oy + k * r)   # s mm out from the chamber face, r mm down from the axis
        d.rectangle([x_face, 120, x_face + 70, Hd - 60], fill="#8E979F")
        d.line([(x_face, 120), (x_face, Hd - 60)], fill="white", width=4)
        d.text((x_face - 150, Hd - 112), "chamber front", font=font(18, True), fill="white")
        d.text((x_face - 150, Hd - 88), "face", font=font(17), fill="white")
        d.polygon([P(0, -40), P(30, -40), P(30, 40), P(0, 40)], fill="#C9CED2", outline="white")
        d.polygon([P(30, -47.5), P(45, -47.5), P(45, 47.5), P(30, 47.5)], fill="#E6E9EB", outline="black")
        d.polygon([P(44, -31.5), P(47, -31.5), P(47, 31.5), P(44, 31.5)], fill="#7FD0F0")
        if cover:
            for sg in (-1, 1):
                d.polygon([P(30, sg * 50), P(30, sg * 81), P(75, sg * 81), P(75, sg * 37.5), P(47, sg * 31.5),
                           P(47, sg * 50)], fill="#4A4F57", outline="white")
            d.polygon([P(15, 81), P(70, 81), P(70, 126), P(15, 126)], fill="#3A3E45", outline="white")
            d.text(P(60, 95), "pod", font=font(17, True), fill="white")
            d.polygon([P(-20, -140), P(55, -140), P(55, -101), P(-20, -101)], fill="#B9C0C6", outline="white")
            d.text(P(52, -133), "furnace foot", font=font(15, True), fill="black")
            d.text(P(52, -116), "bracket", font=font(15, True), fill="black")
            d.text(P(118, -78), "grey cover", font=font(17, True), fill="white")
        else:
            d.text(P(44, -70), "nut", font=font(17, True), fill="white")
        d.text(P(46, 36), "glass", font=font(15, True), fill="#7FD0F0")
        dashed(d, P(-5, 0), P(120, 0), col="#FFD400")
        return P

    def dim(P, mid, s0, s1, r, ext_from=None):
        a, b = P(s0, r), P(s1, r)
        if ext_from is not None:
            for s in (s0, s1):
                dashed(d, P(s, ext_from), P(s, r), col="white", dash=6)
        arrow(d, a, b, cols[mid])
        tag(d, ((a[0] + b[0]) / 2, a[1]), mid, cols[mid], size=21)

    # (a) cover off
    d.text((30, 18), "a) cover off", font=font(24, True), fill="white")
    Pa = panel(560, 420, cover=False)
    dim(Pa, "F13", 0, 45, -75, ext_from=-48)
    dim(Pa, "F13", 0, 45, 75, ext_from=48)
    # F14: a face leaning back from vertical, and a phone lying on it
    cx, cy = 130, 470
    d.line([(cx, cy - 170), (cx, cy + 40)], fill="white", width=2)
    t = math.radians(20)
    top = (cx + 190 * math.sin(t), cy - 190 * math.cos(t))
    d.line([(cx, cy), top], fill="#E6E9EB", width=10)
    ph = [(cx + 40 * math.sin(t) - 10 * math.cos(t), cy - 40 * math.cos(t) - 10 * math.sin(t)),
          (cx + 150 * math.sin(t) - 10 * math.cos(t), cy - 150 * math.cos(t) - 10 * math.sin(t)),
          (cx + 150 * math.sin(t) - 24 * math.cos(t), cy - 150 * math.cos(t) - 24 * math.sin(t)),
          (cx + 40 * math.sin(t) - 24 * math.cos(t), cy - 40 * math.cos(t) - 24 * math.sin(t))]
    d.polygon(ph, fill="#111111", outline="white")
    d.arc([cx - 120, cy - 120, cx + 120, cy + 120], start=-90, end=-90 + 20, fill=cols["F14"], width=6)
    tag(d, (cx + 26, cy - 150), "F14", cols["F14"], size=21)
    label(d, (30, cy + 60), "F14: phone flat on the nut face;", size=16, bold=False)
    label(d, (30, cy + 88), "degrees it leans back from vertical", size=16, bold=False)
    d.text((cx - 6, cy - 200), "vertical", font=font(14), fill="white")
    # (b) cover on
    d.line([(640, 10), (640, Hd - 10)], fill="#566270", width=2)
    d.text((660, 18), "b) cover on", font=font(24, True), fill="white")
    Pb = panel(1160, 430, cover=True)
    dim(Pb, "F16", 0, 75, -150, ext_from=-82)
    dim(Pb, "F9", 47, 75, 0)
    dim(Pb, "F11", 30, 75, 140, ext_from=127)
    a, b = Pb(62, -82), Pb(62, -101)
    arrow(d, a, b, cols["F6"])
    tag(d, (a[0] - 30, (a[1] + b[1]) / 2), "F6", cols["F6"], size=21)
    label(d, (660, Hd - 92), "F9: rule end through the opening to the glass.", size=16, bold=False)
    label(d, (660, Hd - 64), "F11: cover off, face down on a table.", size=16, bold=False)
    label(d, (30, Hd - 44), "Dashed yellow line: the port's axis.", size=16, bold=False)
    return im


def main():
    with open(HERE / "field_sheet.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "priority", "what", "how", "now_in_model", "onshape_variable", "measured", "notes"])
        for sh in SHEETS:
            for mid, pri, title, how, guess, var in sh["rows"]:
                w.writerow([mid, pri, title, how, guess, var, "", ""])
    front_cols = {}
    for sh in SHEETS[:3]:
        front_cols.update(colour_map(sh["rows"]))
    for sh in SHEETS:
        cols = colour_map(sh["rows"])
        if sh["key"] == "4_front_side_sketch":
            photo = front_side_sketch(front_cols)
            rows = []
        elif sh["key"] == "5_left_sight_glass":
            photo = left_port_photo()
            rows = sh["rows"]
        else:
            photo = Image.open(FRAMES / sh["frame"]).convert("RGB")
            rows = sh["rows"]
        s = SCALE.get(sh["key"], 1.0)
        if s != 1.0:
            photo = photo.resize((W, int(photo.height * s)), Image.LANCZOS)
        if sh["key"] in MARKS:
            draw_marks(photo, MARKS[sh["key"]], cols, s)
        parts = [header(sh["title"], sh["where"], sh["src"]), photo]
        if rows:
            parts.append(legend(rows, cols))
        parts.append(footer())
        out = stack(*parts)
        out.save(HERE / f"{sh['key']}.jpg", quality=88)
        print(sh["key"], out.size)


if __name__ == "__main__":
    main()

"""Chapter 3 of the alloy route, start to finish (#303): the atomized powder through the sieving cell, and into the
Aconity MIDI, which prints the plate that ``alloy_workflow.py`` (chapter 4) takes out.

    xvfb-run -a python3 alloy_print.py            # -> out/alloy_print.gif, out/mp4/alloy_print.mp4, .json, still
    PREVIEW=1 xvfb-run -a python3 alloy_print.py  # the last frame of each sub-step -> /tmp/preview_alloy_print.png

It starts where the atomizer chapter ends: the MiR250 parked in front of the AMAZEMET rePowder with the rePowder's
powder container on its cabinet (four 5N Al cups with Si: Al-10Si, ``out/alloy_recipe.json``). It ends where chapter
4 begins: the plate printed and buried in powder in the closed Aconity, the MiR back at x = 1400 with its arm parked,
and chapter 4's opening camera.

The scene is chapter 4's own (``alloy_workflow.build()``: the line, the opened Aconity MIDI, the EDM, the Instrons, the
MiR250 and its UR10e) plus the sieving cell on a bench between the rePowder and the VLM (``sieve_station.py``, round 5):
the Retsch AS 200 control, a tipper over a funnel and five jars, the Al set's stand, a downdraft enclosure. The shaker,
its lid, knobs and the falling fractions are ``instruments_char.sieve()``'s, driven through its own joints; its sieves
are replaced by ``sieve_station``'s, each its own group with a handling tab, so the arm stacks and unstacks them. Every
arm move is a straight line of the gripper or a joint move between two solved poses (``robot.py``). See
``notes/alloy_print.md`` for what is measured and what is assumed.

Round 8 (PR #318): setup_lab's two-Shuttle floor (``alloy_atomize_floor.py``: the Aconity at x = 6950, east of the
second Shuttle); the MiR as chapter 2 leaves it (the empty cup carrier, the container in its low cradle) and the LPBF jar
in a pocket block, no raised holders; the powder grey while it is poured and shaken, coloured by fraction only once it
has settled, with the legend, then grey again; the lab's real sieved jars (DAL #219) after the arm's sieving; and the jar
carried into the MIDI in the IK branch that is clear at the supply cylinder (``alloy_workflow.branch_q``).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pyvista as pv
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

import alloy_workflow as AW           # sets scene.GIF_FPS / GIF_SIZE as chapter 4 does
from scene import CLEAN, PREVIEW, T, R, S, font

import alloy_atomize_floor as FL     # noqa: E402
import alloy_models as M              # noqa: E402
import animate as A                   # noqa: E402
import charge                         # noqa: E402
import instruments_char as IC         # noqa: E402
import line                           # noqa: E402
import props as P                     # noqa: E402
import robot as RB                    # noqa: E402
import sieve_station as SS            # noqa: E402
import tour                           # noqa: E402
from alloy_workflow import held_point, status  # noqa: E402

NAME = "alloy_print"
TITLE = "Vertical cloud lab: from the atomizer's powder to the printed plate"

# ------------------------------------------------------------------------------------------------- layout
BENCH = dict(x=-1982.5, w=1065.0, d=600.0, h=700.0)     # a lab bench between the rePowder and the VLM (assumed)
SIEVE_DX = 11.5                                         # the shaker's centre, from the bench's
TIPPER_DX = -367.5                                      # the tipper's, left of the shaker (sieve_station.py)
STAND_DX = 359.5                                        # the Al set's stand, right of the shaker
GRIP_TAB = 0.88                                         # a sieve's 12 mm handling tab, as the plate's 12 mm lug
GRIP_PAN = 0.69                                         # the pan's tab, held by its sides, 28 mm across (see GR)
OPEN_TAB = 0.5                                          # open only so far for a tab: wide open, the lower finger and
                                                        # its knuckle reach down into the bench or the shaker
CELL_DY = -300.0                                        # the MiR parks 300 mm further off the bench than off the line:
                                                        # nearer, the arm folds into itself to reach the tabs level
HOLDER2_LOCAL = (-190.0, -160.0)                        # the jar's pocket on the MiR's cabinet (MiR frame)
ACO_DY = -250.0                                         # and 250 mm further off the Aconity: from its usual spot the
                                                        # arm reaching into the chamber folded its forearm into the
                                                        # base cabinet; from here it reaches in nearly straight
ENCL_H = 1150.0                                         # the enclosure's height over the bench: at 950 its roof and
                                                        # front rail left the arm no room over the tipper and the knobs
ORDER_UP = ["pan", "s325", "s230", "s140", "s100", "s60"]          # bottom to top on the shaker (instruments_char)
LABEL = {"pan": "pan", "s325": "No. 325", "s230": "No. 230", "s140": "No. 140", "s100": "No. 100", "s60": "No. 60"}
START = (A.REPOWDER_AT[0] + 288.0, -2230.0)             # MiR parked in front of the rePowder's container axis, clear
MIR_END = 1400.0                                        # alloy_workflow.Mir's starting x: chapter 4 begins there
# the MiR's cabinet as chapter 2 (alloy_atomize.py) leaves it: chapter 1's low cup carrier (empty now) and the low
# cradle the container rides in, a ring 37 mm tall on the cabinet top. Round 8: no raised holders on posts any more
# (round 7's low pocketed carrier instead); the LPBF jar rides in a pocket block like the carrier's (props.pocket_block)
CAB_TOP = P.AMR_TOP - 20.0                              # the cabinet's top: the arm stands on a 20 mm plate
CARRIER_AT = (A.BUFFER_LOCAL[0], A.BUFFER_LOCAL[1], CAB_TOP)     # alloy_atomize.CARRIER_AT
CRADLE_AT = (280.0, 10.0, CAB_TOP)                      # alloy_atomize.CRADLE_AT
CRADLE_H = 12.0                                         # alloy_atomize.CRADLE_H
CONT_R_RP = 65.0                                        # the rePowder model's container radius (repowder/model.py)
CRADLE_SEAT = np.array([CRADLE_AT[0], CRADLE_AT[1], CAB_TOP + 3.0])
HOLDER_LOCAL = CRADLE_AT[:2]                            # the container's seat on the MiR (MiR frame)
POCKET_SEAT = np.array([HOLDER2_LOCAL[0], HOLDER2_LOCAL[1], CAB_TOP + P.DECK_FLOOR])   # the jar's base in its pocket
GRIP_HANDLE = 0.876                                     # 12 mm handle bar (alloy_workflow: 0.88 for the 12 mm lug)
GRIP_BAR36 = 0.59                                       # the lid's 36 mm crossbar
GRIP_KNOB = 0.36                                        # the 54 mm knob
GRIP_BOTTLE = 0.18                                      # the 70 mm bottle
LAYER_UM = 50.0                                         # assumed: AddUp's AlSi10Mg sheet (chapter 4) prints 50 um

POWDER = M.POWDER
GREY = POWDER                       # all the powder, in the sieves and the jars, until it has settled (round 8)
STREAM = (0.42, 0.43, 0.46)
PHOTOS = Path(__file__).resolve().parent / "out" / "footage"
SIEVED_PHOTO = dict(file="nab_k7m2q9_sieved_three_jars.jpg",
                    badge="REAL PHOTO · 630 bronze (NAB) · Oct 29 2026 · Gage Erickson, DAL #219",
                    caption="The lab's own sieving, by hand: the Oct 27 bronze runs (lot k7m2q9) in three jars. Left, "
                            "under 63 µm, the LPBF cut: 188 g; middle, 63-250 µm, 827 g; right, flakes over 250 µm, "
                            "182 g; of 1,938 g melted in two runs (Gage Erickson, DAL #219 comment 6509252104).")
BADGE = (178, 34, 34)
LASER = (1.0, 0.45, 0.12)

# the rePowder's container, as instruments_char.sieve() draws it (CONT_LINE, "DAL, assumed size"): Ø128 x 228, a
# handle bar at the top on the -y side. Its own frame: axis on z, base at z = 0
CONT_OUT = [(0.0, 0.0), (54.0, 0.0), (64.0, 10.0), (64.0, 190.0), (44.0, 200.0), (44.0, 228.0)]
HANDLE_GRASP = np.array([45.0, -94.0, 241.0])            # middle of the handle bar
MOUTH = np.array([0.0, 0.0, 228.0])
# a wide-mouth powder bottle (assumed: 250 mL HDPE, Ø70 x 112 with a Ø50 cap)
BOT_R, BOT_H, NECK_R, NECK_H, CAP_H = 35.0, 112.0, 22.0, 12.0, 14.0


def _shell(line_pts, t=1.5):
    """A thin revolved wall along an open (r, z) line, closed into a profile `t` thick (inside)."""
    inner = [(max(r - t, 0.0), z + (t if i == 0 else 0.0)) for i, (r, z) in enumerate(line_pts)]
    prof = list(line_pts) + list(reversed(inner))
    return charge.lathe(prof, res=64)


def container_meshes():
    can = _shell(CONT_OUT)
    collar = charge.lathe([(44.0, 222.0), (52.0, 222.0), (52.0, 249.0), (44.0, 249.0)], res=48)
    arm = pv.Box(bounds=(-8, 8, -88, -44.5, 233, 249)).triangulate()
    bar = pv.Box(bounds=(-4, 85, -100, -88, 235, 247)).triangulate()
    powder = pv.Cylinder(center=(0, 0, 0.5), direction=(0, 0, 1), radius=60.0, height=1.0, resolution=48).triangulate()
    return {"can": (can.merge(collar), (0.80, 0.81, 0.83)), "handle": (arm.merge(bar), (0.78, 0.12, 0.10))}, powder


def bottle_meshes():
    body = charge.lathe([(0, 0), (BOT_R - 4, 0), (BOT_R, 4), (BOT_R, BOT_H - 10), (NECK_R + 2, BOT_H - 2),
                         (NECK_R, BOT_H), (NECK_R, BOT_H + NECK_H), (NECK_R - 2, BOT_H + NECK_H),
                         (NECK_R - 2, BOT_H + 1), (BOT_R - 2, BOT_H - 11), (BOT_R - 2, 3), (0, 3)], res=56)
    cap = charge.lathe([(0, BOT_H + NECK_H - 6), (NECK_R + 3, BOT_H + NECK_H - 6), (NECK_R + 3, BOT_H + NECK_H + CAP_H - 6),
                        (0, BOT_H + NECK_H + CAP_H - 6)], res=48)
    powder = pv.Cylinder(center=(0, 0, 0.5), direction=(0, 0, 1), radius=BOT_R - 2.5, height=1.0,
                         resolution=40).triangulate()
    return body, cap, powder


def cradle_mesh():
    """Chapter 2's container cradle (alloy_atomize.Mir): a low ring and its floor on the cabinet top, MiR frame."""
    cx, cy, cz = CRADLE_AT
    ring = charge.lathe([(CONT_R_RP + 1.0, 0), (CONT_R_RP + 7.0, 0), (CONT_R_RP + 7.0, CRADLE_H + 25.0),
                         (CONT_R_RP + 1.0, CRADLE_H + 25.0)], res=64).translate((cx, cy, cz), inplace=False)
    floor = pv.Cylinder(center=(cx, cy, cz + 1.5), direction=(0, 0, 1), radius=CONT_R_RP + 7.0, height=3.0,
                        resolution=64).triangulate()
    return ring.merge(floor)


def jar_pocket_mesh():
    """A pocket block for the 250 mL LPBF jar, as the cup carrier's (props.pocket_block: 26 mm deep, a lead-in)."""
    hx, hy = HOLDER2_LOCAL
    r = SS.TIP["jar_r"] + P.POCKET_CLEAR
    blk = P.pocket_block(hx - r - 9.0, hx + r + 9.0, hy - r - 9.0, hy + r + 9.0, [(hx, hy, r)])
    return blk.translate((0, 0, CAB_TOP), inplace=False)


def bench_mesh():
    b = BENCH
    x0, x1 = b["x"] - b["w"] / 2, b["x"] + b["w"] / 2
    y0, y1 = line.Y_FACE, line.Y_FACE + b["d"]
    top = pv.Box(bounds=(x0, x1, y0, y1, b["h"] - 30, b["h"])).triangulate()
    legs = None
    for (x, y) in ((x0 + 30, y0 + 30), (x1 - 30, y0 + 30), (x0 + 30, y1 - 30), (x1 - 30, y1 - 30)):
        leg = pv.Box(bounds=(x - 20, x + 20, y - 20, y + 20, 0, b["h"] - 30)).triangulate()
        legs = leg if legs is None else legs.merge(leg)
    shelf = pv.Box(bounds=(x0 + 10, x1 - 10, y0 + 10, y1 - 10, 160, 180)).triangulate()
    return top, legs.merge(shelf)


def build_cell(sc, sv):
    """The sieving cell on the bench (sieve_station.py): the enclosure, the tipper with its funnel and five jars on
    a turntable, the Al set's stand with the set nested on it (storage order), the lid parked on the tipper's roof,
    the ground straps. The LPBF jar is the group "bottle", as the old single bottle was, so step 4 is unchanged."""
    b = BENCH
    sc.frac_col = {}                                      # powder mesh -> its fraction's colour (the legend's)
    y_c = sieve_w(sv, (0, 0, 0))[1]                       # the shaker's centre line: the cell's front-back axis
    zb = b["h"]
    sc.gmat["encl"] = T((b["x"], line.Y_FACE + b["d"] / 2, zb))
    for name, (mesh, col, spec, op) in SS.enclosure_parts(b["w"], b["d"], ENCL_H).items():
        sc.add(f"encl/{name}", mesh, col, "encl", opacity=op, specular=spec)
    # the tipper
    sc.gmat["tipper"] = T((b["x"] + TIPPER_DX, y_c, zb))
    names = {}
    for piece, parts in SS.tipper_parts().items():
        g = "tipper" if piece == "body" else f"tip_{piece}"
        for name, (mesh, col, spec, op) in parts.items():
            sc.add(f"tipper/{piece}/{name}", mesh, col, g, opacity=op, specular=spec)
            names.setdefault(piece, []).append(f"tipper/{piece}/{name}")
    sc.parent["tip_cradle"] = "tipper"
    sc.parent["tip_clamps"] = "tip_cradle"
    sc.parent["tip_knocker"] = "tip_cradle"
    sc.parent["tip_table"] = "tipper"
    # the five jars on the turntable; the LPBF one is "bottle"
    jp = SS.jar_parts()
    for j, (key, txt) in enumerate(SS.JARS):
        g = "bottle" if j == 4 else f"jar{j}"
        for name, (mesh, col, spec, op) in jp.items():
            sc.add(f"{g}/{name}", mesh, col, g, opacity=op, specular=spec)
        pn = "bottle/powder" if j == 4 else f"{g}/powder"
        pg = "bottle_pow" if j == 4 else f"{g}_pow"
        frac_mat = IC.MATERIALS[dict((k, m) for k, _, _, _, m in IC.STACK)["s325" if key == "lpbf" else key]]
        sc.add(pn, SS.jar_powder(), GREY, pg, specular=0.05)        # grey: the colours are only for the legend
        sc.frac_col[pn] = frac_mat[:3]
        sc.parent[pg] = g
        sc.gmat[pg] = T((0, 0, 3.5)) @ S((1, 1, 0.01))
        sc.alpha[pn] = 0.0
        sc.parent[g] = "tip_table"
        x, y = SS.jar_xy(j)
        sc.gmat[g] = T((x, y, 22.0))
    # the stand and the Al set on it, nested No. 60 at the bottom, the pan on top
    sc.gmat["stand"] = T((b["x"] + STAND_DX, y_c, zb))
    for name, (mesh, col, spec, op) in SS.stand_parts().items():
        sc.add(f"stand/{name}", mesh, col, "stand", opacity=op, specular=spec)
    fr = dict((k, m) for k, _, _, _, m in IC.STACK)
    for i, key in enumerate(SS.STORAGE):
        g = f"sv_{key}"
        for name, (mesh, col, spec, op) in SS.sieve_parts(key).items():
            sc.add(f"{g}/{name}", mesh, col, g, opacity=op, specular=spec)
        sc.add(f"{g}/powder", SS.powder_disc(key), GREY, f"{g}_pow", specular=0.05)
        sc.frac_col[f"{g}/powder"] = IC.MATERIALS[fr[key]][:3]
        sc.parent[f"{g}_pow"] = g
        sc.alpha[f"{g}/powder"] = 0.0
        sc.parent[g] = "stand"
        sc.gmat[g] = T((0, 0, SS.STAND["h"] + SS.stand_seat(i)))
    # the lid, parked on the tipper's roof (sieve_station: the arm takes it to the stack and back)
    zl = 212.0 + 6 * IC.DEPTH - 8
    sc.parent["sieve:lid"] = "tipper"
    sc.gmat["sieve:lid"] = T((0, 0, SS.TIP["top"] + 12.0 - zl))
    # ground straps: shaker, tipper, stand, turntable to the bar on the back panel
    gb = np.array([b["x"], line.Y_FACE + b["d"] - 18, zb + 14])
    ends = [sieve_w(sv, (150, 120, 20)), (b["x"] + TIPPER_DX + 140, y_c + 140, zb + 8),
            (b["x"] + STAND_DX + 60, y_c + 100, zb + 8)]
    straps = None
    for e in ends:
        e = np.asarray(e, float)
        s_ = SS.strap(e, (e[0] * 0.5 + gb[0] * 0.5, gb[1], gb[2]))
        straps = s_ if straps is None else straps.merge(s_)
    sc.add("ground straps", straps, (0.35, 0.62, 0.20), "static", specular=0.2)
    sc.tip_names = names
    sc.y_cell = y_c


def stream_pts(top, bottom, t, n=34, on=1.0, spread=2.0):
    """Grains falling from `top` to `bottom` (world), animated by t."""
    s = (np.arange(n) / n + t * 1.9) % 1.0
    s = s[s < on]
    if not len(s):
        return np.zeros((0, 3))
    top, bottom = np.asarray(top, float), np.asarray(bottom, float)
    k = np.arange(len(s))
    xy = top[:2] + (bottom[:2] - top[:2]) * s[:, None] ** 0.6
    xy += np.c_[np.sin(k * 2.3), np.cos(k * 1.7)] * spread
    z = top[2] - (top[2] - bottom[2]) * s ** 2
    return np.c_[xy, z]


# ------------------------------------------------------------------------------------------------- the scene
class PrintScene(AW.AlloyScene):
    """Chapter 4's scene class plus the sieve fractions panel (instruments_char's, drawn on the right)."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.panel_a = 0.0
        self.photo = None                # (PIL image, badge): a real photo shown instead of the model, full frame

    def overlay(self, img, scale, anchors):
        if self.photo is not None:
            pic, badge = self.photo
            img = _fit(pic, img.size)
            keep = self.labels, self.gauges
            self.labels, self.gauges = [], []
            try:
                img = super().overlay(img, scale, [])
            finally:
                self.labels, self.gauges = keep
            if not CLEAN:
                _badge(img, scale, badge)
            return img
        img = super().overlay(img, scale, anchors)
        if not CLEAN and self.panel_a > 0.02:
            _panel(img, scale, self.panel_a)
        return img


def _fit(img, size):
    """`img` inside `size`, on a blurred, darkened copy of itself (alloy_atomize._fit)."""
    bg = ImageOps.fit(img, size, Image.LANCZOS).filter(ImageFilter.GaussianBlur(18))
    bg = ImageEnhance.Brightness(bg).enhance(0.45)
    fg = ImageOps.contain(img, size, Image.LANCZOS)
    bg.paste(fg, ((size[0] - fg.width) // 2, (size[1] - fg.height) // 2))
    return bg


def _badge(img, scale, text):
    """A red badge under the title saying the picture is real (alloy_atomize._dress)."""
    d = ImageDraw.Draw(img, "RGBA")
    s = max(scale, 0.80)
    fb = font(15 * s, bold=True)
    w = d.textlength(text, font=fb)
    d.rounded_rectangle((10 * s, 44 * s, 10 * s + w + 20 * s, 44 * s + 28 * s), 6 * s, fill=(*BADGE, 235))
    d.text((20 * s, 49 * s), text, font=fb, fill=(255, 255, 255))


def _panel(img, scale, alpha):
    """instruments_char._sieve_panel, moved to the top right so the status table stays clear."""
    W, H = img.size
    d = ImageDraw.Draw(img, "RGBA")
    s = max(scale, 0.8)
    a = int(255 * alpha)
    rows = [(f"No. {num}  ({op} um)" if num else "pan", txt, IC.MATERIALS[mat][:3])
            for _, num, op, txt, mat in reversed(IC.STACK)]
    lh, w = 24 * s, 312 * s
    h = (len(rows) + 2) * lh + 38 * s
    x0, y0 = W - w - 0.02 * W, 0.075 * H
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 8 * scale, fill=(255, 255, 255, int(236 * alpha)),
                        outline=(120, 124, 130, a))
    d.text((x0 + 10 * s, y0 + 6 * s), "What stays on each sieve", font=font(14.5 * s, bold=True), fill=(20, 20, 24, a))
    f = font(13 * s)
    for i, (name, txt, col) in enumerate(rows):
        yy = y0 + 32 * s + i * lh
        c = tuple(int(255 * v) for v in col)
        d.ellipse((x0 + 12 * s, yy + 3 * s, x0 + 26 * s, yy + 17 * s), fill=c + (a,))
        d.text((x0 + 34 * s, yy), name, font=f, fill=(20, 20, 24, a))
        d.text((x0 + 180 * s, yy), txt, font=font(13 * s, bold=True), fill=(20, 20, 24, a))
    yy = y0 + 32 * s + len(rows) * lh + 4 * s
    d.text((x0 + 12 * s, yy), "LPBF 20-63 um: No. 325 + pan", font=font(12.5 * s, bold=True), fill=(30, 60, 140, a))
    d.text((x0 + 12 * s, yy + 18 * s), "Amounts drawn are an example, not data", font=font(11.5 * s),
           fill=(150, 30, 30, a))


class Mir2:
    """alloy_workflow.Mir, which drives along x at MIR_Y, given a y as well, for the spot in front of the rePowder
    (whose front stands 300 mm proud of the line's). Off that spot it drives an S-curve with its long axis on the
    tangent, as chapter 2 drives onto it (props.s_curve): a MiR250 is differential drive and can't slide sideways.
    Round 8: PR #321's version, brought over. The old one slid the MiR sideways for the y leg, and drove at about
    twice its published acceleration; now every drive is from rest to rest at 0.3 m/s^2 (props.ramp_frac)."""

    def __init__(self, amr):
        self.amr, self.sc, self.rb = amr, amr.sc, amr.rb
        self.y = AW.MIR_Y

    def place(self, x, y, heading=0.0):
        self.amr.x, self.y = x, y
        self.sc.gmat["amr"] = T((x, y, 0)) @ R((0, 0, 1), heading)
        if self.rb.held is not None:
            self.rb.set()

    def drive(self, x1, y1=None):
        """From rest to rest at the MiR250's 0.3 m/s^2 along the path (props.ramp_frac), over the step's time."""
        y1 = AW.MIR_Y if y1 is None else y1
        at, ps, s = P.s_curve(self.amr.x, self.y, x1, y1)

        def up(u):
            f = P.ramp_frac(P.unease(u), s[-1], AW.MIR_SPEED)
            self.place(*at(float(np.interp(f * s[-1], s, ps))))
        return up

    def secs(self, x1, y1=None):
        s = P.s_curve(self.amr.x, self.y, x1, AW.MIR_Y if y1 is None else y1)[2]
        return max(1.4, P.ramp_secs(s[-1], AW.MIR_SPEED))


def build():
    AW.NAME, AW.TITLE, AW.AlloyScene = NAME, TITLE, PrintScene      # chapter 4's build(), our name and scene class
    with FL.two_shuttle():                  # round 8: setup_lab's floor, two Shuttles, the Aconity at x = 6950
        sc, L, rigs, W, E, amr = AW.build()
    AW.AlloyScene = PrintScene.__mro__[1]
    for key, rig in rigs.items():           # the glovebox, the Instrons and the EDM where setup_lab's floor has them
        sc.gmat[f"{key}:body"] = FL.floor_at(key, rig.inst.bbox())
    # what chapter 5 adds round the old Aconity (the depowdering box, the lance and its post, the rinse cup) and the
    # MiR's plate carrier and bar holder: not in this chapter, and on this floor they stood in front of Shuttle 2
    gone = ("dbox", "lstand/", "lance", "floor pipe", "rinse/", "plate residue")
    fixtures = {f"amr/{nm}" for nm in M.mir_fixtures(amr.top)}
    for nm in list(sc.actors):
        if nm.startswith(gone) or nm in fixtures:
            sc.set_mesh(nm, pv.PolyData())
            sc.alpha[nm] = 0.0
    # the bench and the AS 200 on it
    top, legs = bench_mesh()
    sc.add("bench top", top, (0.28, 0.29, 0.31), "bench", specular=0.2)
    sc.add("bench frame", legs, (0.66, 0.67, 0.70), "bench", specular=0.4)
    inst, ents = tour.load(["sieve"])["sieve"]
    y_s = line.Y_FACE + 60.0 - inst.bbox()[2]
    sv = tour.Rig(sc, inst, ents, "sieve:", at=T((BENCH["x"] + SIEVE_DX, y_s, BENCH["h"])))
    sv.v["~container"] = 1.0 / 0.82                  # its own container: the arm carries ours instead
    sv.v["~carrier"] = 1.0 / 0.82
    sv.apply()
    # the AS 200's own sieves are replaced by ours, each its own group with a handling tab (sieve_station.py)
    for nm in sv.names["stack"]:
        if any(m in nm for m in ("stainless", "sieve_cloth", "brass")):
            sc.set_mesh(nm, pv.PolyData())
    build_cell(sc, sv)
    # the MiR's cups: the container's (it rides back to the rePowder) and the jar's; the container on its cup
    mo = Mir2(amr)
    carrier, _ = charge.carrier()           # chapter 1's cup carrier, empty: the cups went into the crucible
    sc.add("amr/cup carrier", carrier.translate(CARRIER_AT, inplace=False), P.RACK_C, "amr")
    sc.add("amr/cradle", cradle_mesh(), (0.30, 0.32, 0.36), "amr")
    sc.add("amr/jar pocket", jar_pocket_mesh(), P.RACK_C, "amr")
    parts, cpow = container_meshes()
    for name, (mesh, col) in parts.items():
        sc.add(f"pcont/{name}", mesh, col, "pcont", specular=0.5)
    sc.add("pcont/powder", cpow, POWDER, "pcont_pow", specular=0.05)
    sc.parent["pcont_pow"] = "pcont"
    sc.parent["pcont"] = "amr"
    sc.gmat["pcont"] = T(CRADLE_SEAT)       # in chapter 2's cradle, its handle to the front
    # streams and the laser
    sc.add("pstream", pv.PolyData(np.zeros((1, 3))), STREAM, "pstream", style="points", point_size=4.0,
           render_points_as_spheres=True)
    sc.alpha["pstream"] = 0.0
    beam = pv.Cylinder(center=(0, 0, 0.5), direction=(0, 0, 1), radius=1.6, height=1.0, resolution=12).triangulate()
    sc.add("laser beam", beam, LASER, "beam", ambient=1.0, diffuse=0.0, specular=0.0)
    sc.add("melt spot", pv.Sphere(radius=3.5, theta_resolution=12, phi_resolution=8), (1.0, 0.85, 0.55), "spot",
           ambient=1.0, diffuse=0.0, specular=0.0)
    sc.add("scan tracks", pv.PolyData(np.zeros((1, 3))), LASER, "tracks", ambient=1.0, diffuse=0.0, specular=0.0,
           line_width=3.0)
    for n_ in ("laser beam", "melt spot", "scan tracks"):
        sc.alpha[n_] = 0.0
    # the lug that grows during the print (chapter 4's lug is part of the plate group)
    x0, x1, y0, y1, z0, z1 = M.LUG
    sc.add("lug grow", pv.Box(bounds=(x0, x1, y0, y1, 0.0, 1.0)).triangulate(), M.AS_BUILT, "luggrow", specular=0.2)
    sc.parent["luggrow"] = "plate"
    sc.alpha["lug grow"] = 0.0
    mo.place(*START)
    return sc, L, rigs, W, E, amr, sv, mo


# ------------------------------------------------------------------------------------------------- moves
def level_y(p, spin):
    """Gripper level, pointing along +y (towards the machines), turned `spin` degrees about its own axis."""
    return P.tcp_frame(np.asarray(p, float), (0.0, 1.0, 0.0), spin)


def sieve_w(sv, p):
    return (sv.sc.world("sieve:body") @ np.r_[p, 1.0])[:3]


def hatch(z, step=1.6):
    """Scan vectors over the bars' outlines (while the build is under 6 mm) and the lug's, in the plate frame, as
    line segments; returns (bars, lug) point arrays of segment pairs."""
    q = M._half_outline()[:10]                      # the +x, +y quarter: (half width, y), y rising
    qx, qy = np.array([a for a, _ in q]), np.array([b for _, b in q])
    segs = []
    for x in M.BAR_X:
        for y in np.arange(-M.E8_SUB["L"] / 2 + 1, M.E8_SUB["L"] / 2 - 1, step * 2.2):
            w = float(np.interp(abs(y), qy, qx))
            segs.append(((x - w + 0.4, y, z), (x + w - 0.4, y, z)))
    lx0, lx1, ly0, ly1, _, _ = M.LUG
    lug = [((lx0 + 0.5, y, z), (lx1 - 0.5, y, z)) for y in np.arange(ly0 + 1, ly1 - 1, step * 2.0)]
    return segs, lug


def seg_poly(segs):
    if not segs:
        return pv.PolyData(np.zeros((1, 3)))
    pts = np.array([p for s in segs for p in s], float)
    lines = np.hstack([[2, 2 * i, 2 * i + 1] for i in range(len(segs))])
    return pv.PolyData(pts, lines=lines)


# ------------------------------------------------------------------------------------------------- the movie
def movie():
    sc, L, rigs, W, E, amr, sv, mo = build()
    rb = amr.rb
    PARK = np.radians(A.PARK_DEG)
    n = 5
    inst = sv.inst
    zl = 212.0 + 6 * IC.DEPTH - 8                       # the lid's datum (instruments_char.sieve: z_rim - 8)
    z_rim = 212.0 + 6 * IC.DEPTH
    rod_x = 132.0
    rod_top_w = BENCH["h"] + 212.0 + 6 * IC.DEPTH + 50.0    # instruments_char.sieve's rod_top, world
    sv_c = sieve_w(sv, (0, 0, 0))
    aco_bp = W.world(W.bp())
    aco_x = aco_bp[0] - 146.0
    sup = W.world(M.build_point() + (0, M.ACO["sy"] - M.ACO["by"], 0))      # the supply cylinder's axis, floor level
    x_sv = sv_c[0] + 60.0                                                     # MiR at the bench
    y_sv = AW.MIR_Y + CELL_DY
    y_aco = AW.MIR_Y + ACO_DY

    CAM_RP = [(START[0] + 2300, -6400, 2600), (START[0] + 900, -1500, 900), (0, 0, 1)]
    CAM_SV = [tuple(sv_c + (-1250, -1650, 1250)), tuple(sv_c + (0, -120, 420)), (0, 0, 1)]
    CAM_SV_IN = [tuple(sv_c + (-980, -1380, 1000)), tuple(sv_c + (40, -60, 400)), (0, 0, 1)]
    CAM_JAR = [tuple(sv_c + (-700, -2600, 1650)), tuple(sv_c + (220, -560, 320)), (0, 0, 1)]
    CAM_FILL = [tuple(sup + (-420, -1350, 700)), tuple(sup + (0, -160, 40)), (0, 0, 1)]
    CAM_DRIVE = [(2500, -11600, 4600), (2500, -1400, 900), (0, 0, 1)]     # both Shuttles: the cell to the Aconity
    CAM_ACO = [tuple(aco_bp + (-1700, -2300, 1500)), tuple(aco_bp + (100, -520, -120)), (0, 0, 1)]
    CAM_PRINT = [tuple(aco_bp + (-430, -390, 560)), tuple(aco_bp + (10, 40, -15)), (0, 0, 1)]
    CAM_LINE = [(MIR_END + 1700, -10400, 4400), (MIR_END + 1700, -1300, 900), (0, 0, 1)]    # the MiR between the
                                                                                            # two Shuttles

    sc.lid_park = sc.gmat["sieve:lid"].copy()
    sc.lid_parked = True
    frac_col = dict(sc.frac_col)                         # the jars' and the sieves' discs (build_cell)
    for key, _, _, _, mat in IC.STACK:                    # the shaker's own falling clusters (instruments_char.sieve)
        for nm in sv.names.get(f"frac_{key}", []):
            frac_col[nm] = IC.MATERIALS[mat][:3]
    for nm in frac_col:
        sc.color[nm] = GREY

    def lid_fix():
        if sc.lid_parked:
            sc.parent["sieve:lid"] = "tipper"
            sc.gmat["sieve:lid"] = sc.lid_park

    def svmove(t):
        f = sv.move(t)

        def up(u):
            f(u)
            lid_fix()
        return up

    tip_w = sc.world("tipper")[:3, 3]
    stand_w = sc.world("stand")[:3, 3]
    CAM_CELL = [tuple(sv_c + (-420, -2450, 1350)), tuple(sv_c + (-40, 60, 230)), (0, 0, 1)]
    CAM_TIP = [tuple(tip_w + (-560, -1150, 640)), tuple(tip_w + (60, 30, 330)), (0, 0, 1)]
    CAM_STAND = [tuple(stand_w + (650, -1450, 900)), tuple(stand_w + (-260, 40, 360)), (0, 0, 1)]
    status(sc, Arm="UR10e on MiR250, parked", Powder="in the rePowder's container, on the MiR",
           Sieve="the Al set, on its stand", Aconity="idle")
    sc.cam = list(CAM_RP)
    lbl = [A.REPOWDER_LBL[:2] + ((0.12, 0.26),),
           ("sieving cell", tuple(sv_c + (0, 250, 1000)), (0.50, 0.20)),
           ("the rePowder's powder container", tuple(mo.amr.world(CRADLE_SEAT + (0, 0, 260))),
            (0.30, 0.62))]
    cap = "From the atomizer to the printer. The run's powder is in the rePowder's container, on the MiR250: four 5N Al " \
          "cups with Si, Al-10Si, 157 g charged. Next, the sieving cell beside the rePowder, then the Aconity MIDI."
    sc.step(f"1/{n}", cap, 2.4, None, hold=1.4, labels=lbl)

    # ------------------------------------------------------------------ 1. the cell
    cap = "The sieving cell, in a downdraft enclosure, every metal part bonded to a ground bar. Left to right: a " \
          "tipper over a funnel and five labelled jars, the Retsch AS 200, and the Al set's own stand: the lab's 8 in " \
          "stack, No. 60, 100, 140, 230, 325 and the pan (DAL PR #175), nested in reverse, each sieve with a 12 mm " \
          "handling tab at the front."
    status(sc, Arm="driving to the sieving cell")
    sc.step(f"1/{n}", cap, mo.secs(x_sv, y_sv), mo.drive(x_sv, y_sv), hold=2.0, cam_to=CAM_CELL,
            labels=[("tipper, funnel, jars", tuple(tip_w + (0, 0, 640)), (0.14, 0.22)),
                    ("Retsch AS 200 control", tuple(sv_c + (0, -120, 230)), (0.44, 0.16)),
                    ("Al set: No. 60 at the bottom, pan on top", tuple(stand_w + (0, 0, 460)), (0.80, 0.22))])

    def GR(p, key=None):
        # level, pointing at the machines, fingers closing up and down on a tab; the pan's tab is held by its sides:
        # it is the bottom piece on the shaker, and fingers above and below it put the lower one in the shaker's housing
        return level_y(p, 0.0 if key == "pan" else 90.0)

    def tab_now(key):
        return (sc.world(f"sv_{key}") @ np.r_[SS.grasp_local(key), 1.0])[:3]

    def tab_at(parent, M_, key):
        return (sc.world(parent) @ M_ @ np.r_[SS.grasp_local(key), 1.0])[:3]

    def transfer(lab_, cap, key, parent, M_, k=1.0, lift0=26.0, out0=0.0, lift1=26.0, in1=0.0, cam=None,
                 labels=(), up=150.0):
        """Sieve `key` by its tab to M_ in `parent`. out0/in1 > 0: drawn out of / slid into a slot along y (the
        tipper's cradle, under its roof); 0: lifted up and over (the stand; the shaker, between its rods)."""
        g0 = tab_now(key)
        g1 = tab_at(parent, M_, key)
        sc.step(lab_, cap, 1.0 * k, RB.both(rb.joint_to(Tw=GR(g0 - (0, 90, 0), key)), rb.grip_to(OPEN_TAB)),
                hold=0.02, cam_to=cam, labels=labels)
        sc.step(lab_, cap, 0.5 * k, rb.line_to(GR(g0, key)), hold=0.02)
        sc.step(lab_, cap, 0.3 * k, rb.grip_to(GRIP_PAN if key == "pan" else GRIP_TAB), hold=0.02)
        rb.grasp(f"sv_{key}")
        sc.step(lab_, cap, 0.4 * k, rb.line_to(GR(g0 + (0, 0, lift0), key)), hold=0.02)
        a = g0 + ((0, -out0, lift0) if out0 else (0, 0, lift0 + up))
        b = g1 + ((0, -in1, lift1) if in1 else (0, 0, lift1 + up))
        z_over = rod_top_w + 30.0 + SS.tab_z(key)       # the sieve's foot over the shaker's rods
        if not out0:
            a[2] = max(a[2], z_over)
        if not in1:
            b[2] = max(b[2], z_over)
        sc.step(lab_, cap, 0.6 * k, rb.line_to(GR(a, key)), hold=0.02)
        sc.step(lab_, cap, 1.0 * k, rb.joint_to(Tw=GR(b, key)), hold=0.02)
        sc.step(lab_, cap, 0.6 * k, rb.line_to(GR(g1 + (0, 0, lift1), key)), hold=0.02)
        sc.step(lab_, cap, 0.4 * k, rb.line_to(GR(g1, key)), hold=0.02)
        sc.step(lab_, cap, 0.3 * k, rb.grip_to(OPEN_TAB), hold=0.02)
        rb.release(parent)
        sc.gmat[f"sv_{key}"] = M_
        sc.step(lab_, cap, 0.4 * k, rb.line_to(GR(g1 - (0, 90, 0), key)), hold=0.02)

    def on_shaker(i):
        return T((0, 0, 212.0 + SS.stack_seat(i)))

    def on_stand(key):
        return T((0, 0, SS.STAND["h"] + SS.stand_seat(SS.STORAGE.index(key))))

    in_cradle = T((0, 0, SS.TIP["seat"]))

    # ------------------------------------------------------------------ 2. the stack built, the powder in, shaken
    status(sc, Arm="building the stack", Sieve="stacking: pan first")
    cap = "The arm builds the stack on the AS 200. It takes the top piece off the stand by its tab, lifts it clear " \
          "of the one below, draws it out and sets it between the shaker's two rods: the pan first."
    transfer(f"2/{n}", cap, "pan", "sieve:stack", on_shaker(0), k=1.0, cam=CAM_STAND,
             labels=[("handling tab", tuple(tab_now("pan") + (0, -10, 25)), (0.62, 0.30))])
    cap = "Then the No. 325, 230, 140 and 100, and the No. 60 on top: each sieve's skirt nests in the rim below " \
          "(sped up)."
    for i, key in enumerate(ORDER_UP[1:], start=1):
        status(sc, Sieve=f"stacking: {LABEL[key]}")
        transfer(f"2/{n}", cap, key, "sieve:stack", on_shaker(i), k=0.34, cam=CAM_SV if i == 1 else None)
    status(sc, Sieve="stacked: No. 60 to pan", Arm="taking the container")
    # the container: from the MiR's cup, poured onto the No. 60
    g_hold = held_point(sc, "pcont", HANDLE_GRASP)
    cap = "The arm takes the rePowder's container by its handle and tips it into the No. 60. DIN 66165 allows about " \
          "26 cm³ on a 200 mm, 63 um sieve, some 35-40 g of Al powder (DAL PR #175), so a four-cup run goes " \
          "through in about four passes; one is shown."
    sc.step(f"2/{n}", cap, 1.6, RB.both(rb.joint_to(Tw=level_y(g_hold - (0, 140, -40), 90.0)), rb.grip_to(0.0)),
            hold=0.05, cam_to=CAM_SV)
    sc.step(f"2/{n}", cap, 0.9, rb.line_to(level_y(g_hold, 90.0)), hold=0.05)
    sc.step(f"2/{n}", cap, 0.4, rb.grip_to(GRIP_HANDLE), hold=0.05)
    rb.grasp("pcont")
    sc.step(f"2/{n}", cap, 0.8, rb.line_to(level_y(g_hold + (0, 0, 120), 90.0)), hold=0.05)
    th = -115.0                                            # tipped to the right, its body over the stand's side: to
                                                           # the left it swung through the tipper and the parked lid
    m_rel = np.array([-45.0, 94.0, -13.0])                 # mouth from the grasp, upright
    c, s_ = math.cos(math.radians(th)), math.sin(math.radians(th))
    m_rot = np.array([m_rel[0] * c + m_rel[2] * s_, m_rel[1], -m_rel[0] * s_ + m_rel[2] * c])
    target = sieve_w(sv, (30.0, 0.0, z_rim + 100.0))
    p_tip = target - m_rot
    # the container comes to a spot in front of the stack, clear of the sieves' tabs (beside it, it stood in the tipper
    # and the parked lid), tips part way there, then goes in over the No. 60 as it tips the rest of the way: tipped in
    # one move from upright, its foot swept through the tabs
    p_up = p_tip + np.array([0.0, -260.0, 0.0])
    th1 = -70.0
    status(sc, Arm="pouring", Powder="onto the No. 60")
    sc.step(f"2/{n}", cap, 1.8, rb.joint_to(Tw=level_y(p_up, 90.0)), hold=0.05, cam_to=CAM_SV_IN)
    sc.step(f"2/{n}", cap, 0.8, rb.line_to(level_y(p_up, 90.0 + th1)), hold=0.02)
    sc.step(f"2/{n}", cap, 1.2, rb.line_to(level_y(p_tip, 90.0 + th)), hold=0.05)
    heap_in = svmove({f"frac_{k}": (0.0, 1.0) for k, *_ in IC.STACK})

    def pour(u):
        heap_in(min(1.0, u * 1.25))
        sc.gmat["pcont_pow"] = T((0, 0, 4)) @ S((1, 1, max(0.01, 60.0 * (1 - u))))
        sc.alpha["pcont/powder"] = 1.0 if u < 0.97 else 0.0
        mouth = held_point(sc, "pcont", MOUTH)
        pts = stream_pts(mouth, sieve_w(sv, (20, 0, IC.MESH_DZ + z_rim - IC.DEPTH)), u * 5.0,
                         on=1.0 if 0.03 < u < 0.92 else 0.0)
        sc.alpha["pstream"] = 1.0 if len(pts) else 0.0
        if len(pts):
            sc.set_mesh("pstream", pv.PolyData(pts))
    sc.gmat["pcont_pow"] = T((0, 0, 4)) @ S((1, 1, 60.0))
    sc.step(f"2/{n}", cap, 2.4, pour, hold=0.2, live=False)
    sc.alpha["pstream"] = 0.0
    # the empty container back in its cup on the MiR: it rides back to the rePowder to be cleaned
    seat_c = mo.amr.world(CRADLE_SEAT)
    g_back = seat_c + HANDLE_GRASP
    cap = "The empty container goes back in its cup on the MiR, to ride back to the rePowder for cleaning."
    status(sc, Arm="the container back on the MiR", Powder="on the No. 60")
    sc.step(f"2/{n}", cap, 0.8, rb.line_to(level_y(p_up, 90.0 + th1)), hold=0.02)
    sc.step(f"2/{n}", cap, 0.6, rb.line_to(level_y(p_up, 90.0)), hold=0.05)
    sc.step(f"2/{n}", cap, 1.6, rb.joint_to(Tw=level_y(g_back + (0, 0, 120), 90.0)), hold=0.05)
    sc.step(f"2/{n}", cap, 0.8, rb.line_to(level_y(g_back, 90.0)), hold=0.05)
    sc.step(f"2/{n}", cap, 0.4, rb.grip_to(0.0), hold=0.05)
    rb.release("amr")
    sc.step(f"2/{n}", cap, 0.7, rb.line_to(level_y(g_back - (0, 130, -30), 90.0)), hold=0.05)

    # the lid: from the tipper's roof, over the rods and down onto the stack, by its crossbar
    jl = inst.joints["lid"]

    def lid_grasp(v):
        return (sc.world("sieve:stack") @ jl.matrix(v) @ np.r_[0.0, 0.0, zl + 17.0, 1.0])[:3]
    # the lid straight over its seat, its holes over the rods' tops: the corner of the rig's own path, which runs by arc
    # length (lid_grasp(2/3) is still on the way across, so a line from there cut the corner through a rod)
    lid_over = lid_grasp(1.0) + (0.0, 0.0, 212.0 + 6 * IC.DEPTH + 50.0 - zl + 25.0)
    p_lpark = (sc.world("tipper") @ np.r_[0.0, 0.0, SS.TIP["top"] + 29.0, 1.0])[:3]
    cap = "The lid comes off the tipper's roof, over the two rods and down onto the stack, and the arm turns its two " \
          "knobs to clamp it. No shaker found is sold for robot loading, so it does what a person does; Fritsch's " \
          "motor-tensioned ANALYSETTE 3 PRO would take this step out."
    status(sc, Arm="closing the lid")
    sc.step(f"2/{n}", cap, 1.6, rb.joint_to(Tw=A.down(p_lpark + (0, 0, 120), spin=90.0)), hold=0.05, cam_to=CAM_SV)
    sc.step(f"2/{n}", cap, 0.7, rb.line_to(A.down(p_lpark, spin=90.0)), hold=0.05)
    sc.step(f"2/{n}", cap, 0.4, rb.grip_to(GRIP_BAR36), hold=0.05)
    rb.grasp("sieve:lid")
    sc.lid_parked = False
    sc.step(f"2/{n}", cap, 0.7, rb.line_to(A.down(p_lpark + (0, 0, 90), spin=90.0)), hold=0.02)
    sc.step(f"2/{n}", cap, 1.4, rb.joint_to(Tw=A.down(lid_over + (0, 0, 40), spin=90.0)), hold=0.02)
    sc.step(f"2/{n}", cap, 0.5, rb.line_to(A.down(lid_over, spin=90.0)), hold=0.02)
    sc.step(f"2/{n}", cap, 1.0, rb.line_to(A.down(lid_grasp(1.0), spin=90.0)), hold=0.02)
    sc.step(f"2/{n}", cap, 0.4, rb.grip_to(0.0), hold=0.05)
    rb.release("sieve:stack")
    sv.v["lid"] = 1.0
    sv.apply()

    def knobs(a, b, sign):
        for side in ("L", "R"):
            sx = -1 if side == "L" else 1
            # the grasp point near the knob's top (zl + 25 to zl + 47), so the fingertips stay off the crossbar below
            k_top = sieve_w(sv, (sx * rod_x, 0, zl + 48.0))
            sc.step(f"2/{n}", cap, 0.6, rb.line_to(A.down(k_top + (0, 0, 70), spin=90.0)), hold=0.02)
            sc.step(f"2/{n}", cap, 0.35, rb.line_to(A.down(k_top, spin=90.0)), hold=0.02)
            sc.step(f"2/{n}", cap, 0.25, rb.grip_to(GRIP_KNOB), hold=0.02)
            # the gripper holds the knob while it turns it (the knob stays on its rod, so it isn't reparented): a grasp
            # and a release for the audit, as for any part the gripper takes
            rb.events.append((sc.n, "grasp", f"sieve:knob{side}", None))
            q1 = rb.q.copy()
            q1[5] += sign * (-2 * math.pi if q1[5] > 0 else 2 * math.pi)     # one full turn of the wrist
            sc.step(f"2/{n}", cap, 0.8, RB.both(rb.joint_to(q1), svmove({f"knob{side}": (a, b)})), hold=0.02)
            sc.step(f"2/{n}", cap, 0.25, rb.grip_to(0.0), hold=0.02)
            rb.events.append((sc.n, "release", f"sieve:knob{side}", None))
            sc.step(f"2/{n}", cap, 0.35, rb.line_to(A.down(k_top + (0, 0, 70), spin=90.0)), hold=0.02)
    knobs(0.0, 0.5, 1)
    sc.step(f"2/{n}", cap, 1.2, rb.joint_to(PARK), hold=0.05)
    status(sc, Arm="parked", Sieve="lid clamped")

    cap = "Sieving, the stack drawn see-through: 3-D throwing motion, amplitude 0.2-3 mm (Retsch). Each size class " \
          "falls until a cloth stops it. The enclosure draws air down and out through the roof."
    status(sc, Sieve="shaking")
    sv_names = [f"sv_{k}" for k in ORDER_UP]

    def see_through(f1):
        f0 = getattr(sc, "_svg", 0.0)

        def up(u):
            sc._svg = f0 + (f1 - f0) * u
            for g in sv_names:
                for nm in sc.members(g):
                    if "powder" not in nm:
                        sc.alpha[nm] = 1.0 - 0.75 * sc._svg
        return up
    sc.step(f"2/{n}", cap, 1.2, RB.both(svmove({"~lid": (0.0, 1.0), "~knobL": (0.0, 1.0), "~knobR": (0.0, 1.0)}),
                                        see_through(1.0)), hold=0.05, cam_to=CAM_SV_IN)
    sc.step(f"2/{n}", cap, 5.0, svmove({"stack": (0.0, 1.0), **{f"fall_{k}": (0.0, 1.0) for k, *_ in IC.STACK}}),
            hold=0.1)

    sc.step(f"2/{n}", "Settled: the shaker stops, and every grain is on the cloth that stopped it.", 0.4, None,
            hold=1.0)

    def tint(f1, show_panel):
        """Every powder mesh from its current mix towards its fraction's colour (f = 1) or grey (0); the legend with
        it. All grey while it is poured and shaken: it is one powder; coloured only once it has settled."""
        f0 = getattr(sc, "_tint", 0.0)

        def up(u):
            f = f0 + (f1 - f0) * u
            sc._tint = f
            for nm, c in frac_col.items():
                sc.color[nm] = tuple(g_ + (c_ - g_) * f for g_, c_ in zip(GREY, c))
            sc.panel_a = f if show_panel else sc.panel_a
        return up
    status(sc, Sieve="done: six fractions")
    cap = "Coloured now only to tell them apart: the fractions, by the sieve that keeps each. The LPBF cut, 20-63 um, " \
          "is the No. 325 and the pan: there is no 20 um sieve, and DAL found under 20 um is about 0.05 % by mass."
    sc.step(f"2/{n}", cap, 0.8, tint(1.0, True), hold=3.4,
            labels=[("No. 325 (45 um)", tuple(sieve_w(sv, (IC.RW + IC.LIP, 0, 212.0 + IC.DEPTH + 10))), (0.40, 0.70)),
                    ("pan", tuple(sieve_w(sv, (IC.RW + IC.LIP, 0, 212.0 + 10))), (0.40, 0.80))])
    cap = "And back to grey: it is all the same powder, only sorted by size."
    sc.step(f"2/{n}", cap, 0.8, tint(0.0, True), hold=0.6, labels=[])
    sc.panel_a = 0.0
    # each fraction now rides on its own sieve
    for key in ORDER_UP:
        sv.v[f"frac_{key}"] = 0.0
        sc.alpha[f"sv_{key}/powder"] = 1.0
    sv.apply()

    def panel_off(u):
        sc.panel_a = 0.0

    # ------------------------------------------------------------------ 3. the stack taken apart, each fraction to its jar
    cap = "Now the part the lab does by hand (Gage Erickson's videos of 29 Oct): the arm unclamps the lid and puts it " \
          "back on the tipper's roof."
    status(sc, Arm="unclamping", Sieve="unclamped")
    sc.step(f"3/{n}", cap, 1.0, RB.both(svmove({"~lid": (1.0, 0.0), "~knobL": (1.0, 0.0), "~knobR": (1.0, 0.0)}),
                                        see_through(0.0), panel_off),
            hold=0.05, cam_to=CAM_SV, labels=[])
    sc.panel_a = 0.0
    sc.step(f"3/{n}", cap, 1.4, rb.joint_to(Tw=A.down(sieve_w(sv, (-rod_x, 0, zl + 48.0)) + (0, 0, 70), spin=90.0)),
            hold=0.02)
    knobs(0.5, 0.0, -1)
    sc.step(f"3/{n}", cap, 0.8, rb.line_to(A.down(lid_grasp(1.0) + (0, 0, 60), spin=90.0)), hold=0.02)
    sc.step(f"3/{n}", cap, 0.5, rb.line_to(A.down(lid_grasp(1.0), spin=90.0)), hold=0.02)
    sc.step(f"3/{n}", cap, 0.4, rb.grip_to(GRIP_BAR36), hold=0.05)
    rb.grasp("sieve:lid")
    sc.step(f"3/{n}", cap, 1.0, rb.line_to(A.down(lid_over, spin=90.0)), hold=0.02)
    sc.step(f"3/{n}", cap, 0.5, rb.line_to(A.down(lid_over + (0, 0, 40), spin=90.0)), hold=0.02)
    sc.step(f"3/{n}", cap, 1.4, rb.joint_to(Tw=A.down(p_lpark + (0, 0, 90), spin=90.0)), hold=0.02)
    sc.step(f"3/{n}", cap, 0.7, rb.line_to(A.down(p_lpark, spin=90.0)), hold=0.02)
    sc.step(f"3/{n}", cap, 0.4, rb.grip_to(0.0), hold=0.05)
    rb.release("tipper")
    sc.lid_parked = True
    lid_fix()
    sc.step(f"3/{n}", cap, 0.6, rb.line_to(A.down(p_lpark + (0, 0, 120), spin=90.0)), hold=0.05)

    # the jars, labelled
    jar_lbl = []
    for j, (key, txt) in enumerate(SS.JARS):
        g = "bottle" if j == 4 else f"jar{j}"
        jar_lbl.append((txt, tuple(sc.world(g)[:3, 3] + (0, -40, 150)), (0.06 + 0.12 * j, 0.80)))
    table = {"deg": 0.0}

    def table_to(j):
        d0, d1 = table["deg"], -72.0 * j

        def up(u):
            table["deg"] = d0 + (d1 - d0) * u
            sc.gmat["tip_table"] = R((0, 0, 1), table["deg"], (0.0, SS.TIP["table_dy"], 0.0))
        return up
    jar_fill = {j: 0.0 for j in range(5)}
    share = {"s60": 10.0, "s100": 16.0, "s140": 24.0, "s230": 30.0, "s325": 30.0, "pan": 28.0}   # mm drawn: example
    zc = SS.TIP["zc"]

    def flip(key, k=1.0, cap="", lab_=f"3/{n}"):
        j = SS.JAR_OF[key]
        g = "bottle" if j == 4 else f"jar{j}"
        pg = "bottle_pow" if j == 4 else f"{g}_pow"
        pn = "bottle/powder" if j == 4 else f"{g}/powder"
        h0, h1 = jar_fill[j], jar_fill[j] + share[key]
        jar_fill[j] = h1
        top = (sc.world("tipper") @ np.r_[0.0, 0.0, zc - 40.0, 1.0])[:3]
        bot = (sc.world("tipper") @ np.r_[0.0, 0.0, SS.TIP["jar_h"] + 26.0, 1.0])[:3]

        def clamp(f0, f1):
            def up(u):
                kk = 1.0 - (4.0 / 113.0) * (f0 + (f1 - f0) * u)
                sc.gmat["tip_clamps"] = S((kk, kk, 1.0))
            return up

        def over(u):
            ang = 180.0 * u
            sc.gmat["tip_cradle"] = R((1, 0, 0), ang, (0.0, 0.0, zc))
            fall = min(1.0, max(0.0, (ang - 100.0) / 60.0))
            sc.alpha[f"sv_{key}/powder"] = 1.0 - fall
            sc.alpha[pn] = 1.0 if (h0 > 0.5 or fall > 0) else 0.0
            sc.gmat[pg] = T((0, 0, 3.5)) @ S((1, 1, max(0.01, h0 + (h1 - h0) * fall)))
            pts = stream_pts(top, bot, u * 4.0, on=1.0 if 0.0 < fall < 1.0 else 0.0, spread=6.0)
            sc.alpha["pstream"] = 1.0 if len(pts) else 0.0
            if len(pts):
                sc.set_mesh("pstream", pv.PolyData(pts))

        def knock(u):
            sc.gmat["tip_knocker"] = T((-3.5 * abs(math.sin(math.pi * u * 6.0)), 0, 0))
            sc.gmat["tip_cradle"] = R((1, 0, 0), 180.0, (0.0, 0.0, zc)) @ T((0, 0, 0.8 * math.sin(math.pi * u * 12)))

        def back(u):
            sc.gmat["tip_cradle"] = R((1, 0, 0), 180.0 * (1 - u), (0.0, 0.0, zc))
        sc.step(lab_, cap, 0.35 * k, clamp(0.0, 1.0), hold=0.02)
        sc.step(lab_, cap, 1.3 * k, over, hold=0.02, live=False)
        sc.alpha["pstream"] = 0.0
        sc.step(lab_, cap, 0.9 * k, knock, hold=0.02)
        sc.gmat["tip_knocker"] = np.eye(4)
        sc.step(lab_, cap, 1.0 * k, back, hold=0.02)
        sc.step(lab_, cap, 0.3 * k, clamp(1.0, 0.0), hold=0.02)

    for i, key in enumerate(reversed(ORDER_UP)):
        first = i == 0
        k = 1.0 if first else 0.34
        j = SS.JAR_OF[key]
        if first:
            cap = "The No. 60 comes off the top, out between the rods and into the tipper's cradle, which is open at " \
                  "the front for the tab. The cradle clamps the frame."
        else:
            cap = "The same for the No. 100, 140, 230, 325 and the pan, top down, each into its own jar; the No. 325 " \
                  "and the pan both into the LPBF jar (sped up)."
        status(sc, Arm="taking the stack apart", Sieve=f"{LABEL[key]}: to the tipper")
        if table["deg"] != -72.0 * j:
            sc.step(f"3/{n}", cap, 0.7 * k, table_to(j), hold=0.02)
        transfer(f"3/{n}", cap, key, "tip_cradle", in_cradle, k=k, lift0=26.0, out0=0.0, lift1=58.0, in1=200.0,
                 cam=CAM_TIP if first else (CAM_SV if i == 1 else None), labels=jar_lbl if first else ())
        if first:
            cap = "The cradle turns the sieve over the funnel, and a pneumatic knocker taps the frame, not the cloth " \
                  "(DAL #234: tap the frame; no brush on 63 um or finer, no air jet on any cloth). The fraction runs " \
                  "down the funnel into its labelled jar."
        status(sc, Sieve=f"{LABEL[key]}: tipped into the {SS.JARS[j][1]} jar", Arm="waiting")
        sc.step(f"3/{n}", cap, 0.6 * k, rb.joint_to(Tw=GR(tab_at("tip_cradle", in_cradle, key) - (0, 260, -60), key)),
                hold=0.02)
        flip(key, k=k, cap=cap)
        if first:
            cap = "Empty, it goes back on the stand, the first of the set again: put back top down, the set ends in " \
                  "storage order for the next run. Between alloys it would go to an ultrasonic bath first."
        status(sc, Sieve=f"{LABEL[key]}: back on the stand", Arm="putting the sieve back")
        transfer(f"3/{n}", cap, key, "stand", on_stand(key), k=k, lift0=58.0, out0=200.0, lift1=26.0, in1=0.0,
                 cam=CAM_STAND if first else None)
    status(sc, Sieve="the set back on its stand", Powder="five fractions in five jars")
    pic = PHOTOS / SIEVED_PHOTO["file"]
    if pic.exists():                                      # the lab's real result, after the model's sieving
        sc.photo = (ImageOps.exif_transpose(Image.open(pic)).convert("RGB"), SIEVED_PHOTO["badge"])
        sc.step(f"3/{n}", SIEVED_PHOTO["caption"], 0.3, None, hold=5.0, labels=[])
        sc.photo = None

    # the LPBF jar to the MiR's second cup. The MiR first rolls 300 mm back up to its usual line: from the cell's spot
    # the reach down to the jar under the funnel put the forearm in the bench's front edge
    cap = "The arm parks and the MiR250 pulls up to the bench for the jar under the funnel: forward onto its usual " \
          "line, then back along it. It can't drive sideways."
    sc.step(f"3/{n}", cap, 1.2, rb.joint_to(PARK), hold=0.05)
    # round 8: these 300 mm were a sideways slide, which a differential-drive MiR250 can't do: now a short S-curve
    # forward onto the line (at most 27 degrees off it), then straight back, each from rest to rest at 0.3 m/s^2
    x_fwd = x_sv + 900.0
    sc.step(f"3/{n}", cap, mo.secs(x_fwd, AW.MIR_Y), mo.drive(x_fwd, AW.MIR_Y), hold=0.05)
    sc.step(f"3/{n}", cap, mo.secs(x_sv, AW.MIR_Y), mo.drive(x_sv, AW.MIR_Y), hold=0.05)
    b_seat = sc.world("bottle")[:3, 3]
    b_grasp = b_seat + (0, 0, 58.0)
    seat2 = mo.amr.world(POCKET_SEAT)
    cap = "The arm draws the LPBF jar out from under the funnel and stands it in a cup on the MiR. The lab weighs " \
          "and labels each jar now; here the label is printed before the run."
    status(sc, Arm="taking the LPBF jar")
    sc.step(f"3/{n}", cap, 1.6, RB.both(rb.joint_to(Tw=level_y(b_grasp - (0, 160, 0), 0.0)), rb.grip_to(0.0)),
            hold=0.05, cam_to=CAM_TIP, labels=jar_lbl)
    sc.step(f"3/{n}", cap, 0.9, rb.line_to(level_y(b_grasp, 0.0)), hold=0.05)
    sc.step(f"3/{n}", cap, 0.4, rb.grip_to(GRIP_BOTTLE), hold=0.05)
    rb.grasp("bottle")
    sc.step(f"3/{n}", cap, 0.9, rb.line_to(level_y(b_grasp - (0, 170, -10), 0.0)), hold=0.05)
    sc.step(f"3/{n}", cap, 1.6, rb.joint_to(Tw=level_y(seat2 + (0, 0, 58.0 + 110), 0.0)), hold=0.05, labels=[])
    sc.step(f"3/{n}", cap, 0.8, rb.line_to(level_y(seat2 + (0, 0, 58.0), 0.0)), hold=0.05)
    sc.step(f"3/{n}", cap, 0.4, rb.grip_to(0.0), hold=0.05)
    rb.release("amr")
    sc.step(f"3/{n}", cap, 0.7, rb.line_to(level_y(seat2 + (0, -140, 58.0), 0.0)), hold=0.05)
    sc.step(f"3/{n}", cap, 1.2, rb.joint_to(PARK), hold=0.05)
    status(sc, Arm="parked", Powder="< 63 um, in the jar on the MiR")

    # ------------------------------------------------------------------ 4. to the Aconity; into the powder supply
    cap = f"To the Aconity MIDI, {(aco_x - x_sv) / 1000:.1f} m along the row, past both Kardex Shuttles' openings."
    status(sc, Arm="driving to the Aconity MIDI")
    sc.step(f"4/{n}", cap, mo.secs(aco_x, y_aco), mo.drive(aco_x, y_aco), hold=0.2, cam_to=CAM_DRIVE)
    cap = "The door opens, and the chamber is drawn see-through. The MIDI's 170 mm build cylinder is at the front; " \
          "the 170 mm powder supply cylinder is behind it (DAL PR #169). Its piston drops to take the powder."
    status(sc, Aconity="door open, supply down")
    sup_drop = 70.0

    def supply_down(u):
        sc.gmat["aco_supply"] = T((0, 0, -sup_drop * u))
    sc.step(f"4/{n}", cap, 1.6, RB.both(W.door(1.0), W.ghost(1.0)), hold=0.1, cam_to=CAM_ACO,
            labels=[("powder supply, 170 mm", tuple(sup + (0, 0, 40)), (0.16, 0.34)),
                    ("build cylinder, 170 mm", tuple(aco_bp + (0, 0, -40)), (0.18, 0.62))])
    sc.step(f"4/{n}", cap, 1.0, supply_down, hold=0.1)
    # take the bottle again, carry it in level, over the supply, and tip it
    seat_now = held_point(sc, "bottle", (0, 0, 58.0))
    cap = "The arm carries the jar in, level, over the supply cylinder, and turns its wrist to pour. A full MIDI " \
          "build cylinder takes about 440 g of powder, and its 55 mm reduction kit about 30 g (DAL #138). Four cups " \
          "make 157 g of charge; the 225 cm³ crucible has taken 1,080 g of 630 bronze in one run (DAL #219)."
    status(sc, Arm="filling the supply")
    sc.step(f"4/{n}", cap, 1.4, RB.both(rb.joint_to(Tw=level_y(seat_now - (0, 150, 0), 0.0)), rb.grip_to(0.0)),
            hold=0.05, cam_to=CAM_FILL)
    sc.step(f"4/{n}", cap, 0.8, rb.line_to(level_y(seat_now, 0.0)), hold=0.05)
    sc.step(f"4/{n}", cap, 0.4, rb.grip_to(GRIP_BOTTLE), hold=0.05)
    rb.grasp("bottle")
    sc.step(f"4/{n}", cap, 0.8, rb.line_to(level_y(seat_now + (0, 0, 150), 0.0)), hold=0.05)
    door_front = W.world(np.array(M.door_pivot()))[1]
    # the jar's foot 32 mm over the chamber floor (the grasp is 58 mm up the jar), 60 mm short of the supply's axis:
    # tipped, the mouth is over the cylinder
    p_in0 = np.array([sup[0] - 60.0, door_front - 150.0, sup[2] + 90.0])
    p_pour = np.array([sup[0] - 60.0, sup[1] - 60.0, sup[2] + 90.0])
    # round 8: to the door in the IK branch that is clear at the cylinder (alloy_workflow.branch_q), then straight in.
    # Round 7 went in by a planned joint move from the branch it had at the door, which the planner couldn't route
    # through the 280 mm opening, so its fallback put the forearm in the base cabinet (97 frames)
    q_in0 = AW.branch_q(rb, level_y(p_in0, 0.0), level_y(p_pour, 0.0))
    sc.step(f"4/{n}", cap, 1.8, rb.joint_to(q1=q_in0), hold=0.05)
    sc.step(f"4/{n}", cap, 1.6, rb.line_to(level_y(p_pour, 0.0)), hold=0.05)
    sc.step(f"4/{n}", cap, 1.0, rb.line_to(level_y(p_pour, 112.0)), hold=0.05)

    def fill(u):
        sc.gmat["bottle_pow"] = T((0, 0, 3.5)) @ S((1, 1, max(0.01, 58.0 * (1 - u))))
        sc.alpha["bottle/powder"] = 1.0 if u < 0.97 else 0.0
        sc.gmat["aco_supply"] = T((0, 0, -sup_drop * (1 - u)))
        mouth = held_point(sc, "bottle", (0, 0, BOT_H + NECK_H))
        pts = stream_pts(mouth, (mouth[0] + 8, mouth[1], sup[2] - sup_drop * (1 - u) - 1), u * 5.0,
                         on=1.0 if 0.03 < u < 0.93 else 0.0)
        sc.alpha["pstream"] = 1.0 if len(pts) else 0.0
        if len(pts):
            sc.set_mesh("pstream", pv.PolyData(pts))
    sc.step(f"4/{n}", cap, 2.4, fill, hold=0.2, live=False)
    sc.alpha["pstream"] = 0.0
    status(sc, Aconity="supply filled")
    cap = "The empty jar goes back on the MiR, and the door shuts. The chamber is purged with argon before the " \
          "laser runs."
    sc.step(f"4/{n}", cap, 0.8, rb.line_to(level_y(p_pour, 0.0)), hold=0.05)
    sc.step(f"4/{n}", cap, 1.4, rb.line_to(level_y(p_in0, 0.0)), hold=0.05)          # straight out, same branch
    sc.step(f"4/{n}", cap, 1.6, rb.joint_to(Tw=level_y(seat_now + (0, 0, 150), 0.0)), hold=0.05)
    sc.step(f"4/{n}", cap, 0.8, rb.line_to(level_y(seat_now, 0.0)), hold=0.05)
    sc.step(f"4/{n}", cap, 0.4, rb.grip_to(0.0), hold=0.05)
    rb.release("amr")
    sc.step(f"4/{n}", cap, 0.7, rb.line_to(level_y(seat_now - (0, 140, 0), 0.0)), hold=0.05)
    status(sc, Arm="parked", Powder="in the MIDI's supply")
    sc.step(f"4/{n}", cap, 1.4, RB.both(rb.joint_to(PARK), W.door(0.0)), hold=0.2)

    # ------------------------------------------------------------------ 5. the print, as a time-lapse
    layers = int(round(W.build_h * 1000.0 / LAYER_UM))
    cap = f"The print, sped up and cut open: the recoater spreads a layer from the supply over the build cylinder, " \
          f"the laser melts the bars' and the lug's outlines, the platform drops one layer. {layers} layers of " \
          f"{LAYER_UM:.0f} um (assumed) make the {W.build_h:.0f} mm build."
    status(sc, Aconity="printing (argon)", Arm="parked; free for other work")
    plate_top0 = W.floor
    W.set_piston(plate_top0 - M.PLATE["t"])
    bar_groups = [f"bar{k}" for k in range(4)]
    sc.alpha["plate/lug"] = 0.0
    bar_names = [f"bar{k}/a" for k in range(4)] + [f"bar{AW.TEST}/b"]
    for nm in bar_names + ["lug grow"]:
        sc.alpha[nm] = 0.0                      # nothing on the plate before the first layer
    for g in bar_groups:
        sc.gmat[g] = T((M.BAR_X[int(g[3:])], 0, 0)) @ S((1, 1, 0.01))
    sc.gmat["luggrow"] = S((1, 1, 0.01))
    beam_top = W.world(M.build_point(M.ACO["floor"] + 270.0))
    segs_b, segs_l = hatch(0.0)
    cycles = 6
    rec_dy = -420.0

    def print_up(u):
        h = W.build_h * min(1.0, u * 1.0)
        W.set_piston(W.floor - M.PLATE["t"] - h)
        sc.alpha["aco powder cake"] = 0.38 if h > 0.6 else 0.0
        sb = min(1.0, h / M.E8_SUB["T"])
        for nm in bar_names + ["lug grow"]:
            sc.alpha[nm] = 1.0 if h > 0.05 else 0.0
        for g in bar_groups:
            sc.gmat[g] = T((M.BAR_X[int(g[3:])], 0, 0)) @ S((1, 1, max(0.01, sb)))
        sc.gmat["luggrow"] = S((1, 1, max(0.01, h)))
        c_ = (u * cycles) % 1.0
        if u >= 1.0:
            c_ = 1.0
        # recoat in the first 35 % of each cycle: to the front and back; then the scan
        if c_ < 0.35:
            w_ = c_ / 0.35
            sc.gmat["aco_recoater"] = T((0, rec_dy * math.sin(math.pi * w_), 0))
            on = False
        else:
            sc.gmat["aco_recoater"] = np.eye(4)
            on = u < 1.0
        segs = (segs_b if h < M.E8_SUB["T"] else []) + segs_l
        k = int(len(segs) * min(1.0, (c_ - 0.35) / 0.6)) if on else 0
        for nm in ("laser beam", "melt spot", "scan tracks"):
            sc.alpha[nm] = 1.0 if on and k > 0 else 0.0
        if on and k > 0:
            plate_w = sc.world("plate")
            pts = [((plate_w @ np.r_[a[0], a[1], h + 0.25, 1.0])[:3], (plate_w @ np.r_[b[0], b[1], h + 0.25, 1.0])[:3])
                   for a, b in segs[:k]]
            sc.set_mesh("scan tracks", seg_poly(pts))
            spot = pts[-1][1]
            sc.gmat["spot"] = T(spot)
            sc.gmat["beam"] = T(spot) @ S((1, 1, max(1.0, beam_top[2] - spot[2])))
        status(sc, Aconity=f"printing, layer {int(layers * min(1.0, u)):d} of {layers}")
    sc.step(f"5/{n}", cap, 1.4, W.ghost(1.0), hold=0.05, cam_to=CAM_PRINT,
            labels=[("recoater", tuple(W.world(M.build_point() + (0, 300, 40))), (0.70, 0.30)),
                    ("build platform", tuple(aco_bp + (0, 0, -20)), (0.18, 0.62))])
    handle = [nm for nm in W.names["door"] if "printer_black" in nm]     # the door's handle: in front of the plate
    for nm in handle:
        sc.alpha[nm] = 0.0
    lbl_laser = [("laser (beam drawn)", tuple(beam_top), (0.70, 0.18))]
    if PREVIEW:                     # a frame mid-scan in the preview sheet as well
        sc.step(f"5/{n}", cap, 4.0, lambda e: print_up(0.45 * e), hold=0.0, labels=lbl_laser)
        sc.step(f"5/{n}", cap, 5.0, lambda e: print_up(0.45 + 0.55 * e), hold=0.4, labels=lbl_laser)
    else:
        sc.step(f"5/{n}", cap, 9.0, print_up, hold=0.4, labels=lbl_laser)
    for nm in ("laser beam", "melt spot", "scan tracks"):
        sc.alpha[nm] = 0.0
    sc.gmat["aco_recoater"] = np.eye(4)
    for g in bar_groups:
        sc.gmat[g] = T((M.BAR_X[int(g[3:])], 0, 0))
    sc.alpha["plate/lug"] = 1.0
    for nm in bar_names:
        sc.alpha[nm] = 1.0
    sc.alpha["lug grow"] = 0.0
    W.set_piston(W.floor - W.build_h - M.PLATE["t"])
    status(sc, Aconity="print done, under powder")

    cap = "Printed: four ASTM E8 subsize bars and a handling lug on the 170 mm plate, buried in powder. The MiR " \
          "comes back along the line. Chapter 4 checks the sieved powder; chapter 5 takes the plate from here."

    sc.step(f"5/{n}", cap, 1.2, W.ghost(0.0), hold=0.1, cam_to=CAM_ACO)
    status(sc, Arm="UR10e on MiR250, parked", Powder="", Sieve="", Aconity="", Plate="in the Aconity MIDI")
    sc.step(f"5/{n}", cap, mo.secs(MIR_END), mo.drive(MIR_END), hold=0.2, cam_to=CAM_LINE)
    sc.step(f"5/{n}", cap, 0.6, None, hold=1.6, still=True,
            labels=[("Aconity MIDI metal printer", (line.LINE["aconity"], line.Y_FACE + 300, 2400), (0.22, 0.20)),
                     ("UR10e on a MiR250", tuple(amr.world((0, 0, 1300))), (0.10, 0.45))])
    print(f"highest forearm/wrist point {rb.max_z_world:.0f} mm", flush=True)
    info = sc.save()
    return info


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] not in ("movie",):
        raise SystemExit(__doc__)
    print(movie(), flush=True)
